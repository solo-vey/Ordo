from __future__ import annotations

from typing import Any
from datetime import datetime, timezone
import secrets


def namespace_id(package: str, local_id: str) -> str:
    if "." in local_id and local_id.startswith(package + "."):
        return local_id
    return f"{package}.{local_id}"




class FlowReuseCompileError(ValueError):
    """Raised when an authored optional flow-reuse construct is invalid."""


def _qualified(namespace: str, local_id: str) -> str:
    if not namespace or not local_id:
        raise FlowReuseCompileError("namespace and identifier must be non-empty")
    if local_id.startswith(namespace + "."):
        return local_id
    return f"{namespace}.{local_id}"


def _validate_one_to_one(mapping: dict[str, str], label: str) -> None:
    values = list(mapping.values())
    if len(values) != len(set(values)):
        raise FlowReuseCompileError(f"{label} must be one-to-one")


def lower_flow_reuse(source: dict[str, Any], package: str) -> list[dict[str, Any]]:
    """Resolve optional FLOW.JOIN / SHARED.TAIL.REFERENCE into graph IR.

    The lowering is author-triggered only. It never detects or rewrites duplicated tails.
    """
    block = source.get("flow_reuse") or {}
    joins = block.get("joins") or []
    tails = block.get("shared_tails") or []
    refs = block.get("references") or []
    if not (joins or tails or refs):
        return []

    seen: set[str] = set()
    tail_index: dict[tuple[str, str], dict[str, Any]] = {}
    ops: list[dict[str, Any]] = []

    for tail in tails:
        tid, ns = tail.get("id"), tail.get("namespace")
        key = (ns, tid)
        qid = _qualified(ns, tid)
        if qid in seen:
            raise FlowReuseCompileError(f"duplicate flow reuse id: {qid}")
        seen.add(qid)
        nodes = tail.get("nodes") or []
        entry = tail.get("entry")
        if not nodes or entry not in nodes:
            raise FlowReuseCompileError(f"shared tail {qid} entry must be listed in nodes")
        resolved_nodes = [_qualified(ns, n) for n in nodes]
        tail_index[key] = tail
        ops.append({
            "op": "SHARED.TAIL.DEF",
            "id": qid,
            "source_local_id": tid,
            "namespace": ns,
            "entry": _qualified(ns, entry),
            "nodes": resolved_nodes,
            "maturity": tail.get("maturity", block.get("maturity", "experimental_optional")),
        })

    # Optional nested tail dependencies are resolved as a DAG. They are not
    # required by the authoring syntax, but when present they must not recurse.
    dependency_graph: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for key, tail in tail_index.items():
        deps: list[tuple[str, str]] = []
        for dep in tail.get("references", []) or []:
            dep_ns = dep.get("tail_namespace") or key[0]
            dep_id = dep.get("tail_id")
            dep_key = (dep_ns, dep_id)
            if dep_key not in tail_index:
                raise FlowReuseCompileError(
                    f"shared tail {_qualified(key[0], key[1])} references missing tail {dep_ns}.{dep_id}"
                )
            deps.append(dep_key)
        dependency_graph[key] = deps

    visiting: set[tuple[str, str]] = set()
    visited: set[tuple[str, str]] = set()

    def visit_tail(key: tuple[str, str], path: list[tuple[str, str]]) -> None:
        if key in visiting:
            cycle = path[path.index(key):] + [key]
            rendered = " -> ".join(_qualified(ns, tid) for ns, tid in cycle)
            raise FlowReuseCompileError(f"recursive shared-tail reference: {rendered}")
        if key in visited:
            return
        visiting.add(key)
        path.append(key)
        for dep in dependency_graph.get(key, []):
            visit_tail(dep, path)
        path.pop()
        visiting.remove(key)
        visited.add(key)

    for key in dependency_graph:
        visit_tail(key, [])

    for join in joins:
        jid, ns = join.get("id"), join.get("namespace")
        qid = _qualified(ns, jid)
        if qid in seen:
            raise FlowReuseCompileError(f"duplicate flow reuse id: {qid}")
        seen.add(qid)
        incoming = join.get("incoming") or []
        if len(incoming) < 2:
            raise FlowReuseCompileError(f"join {qid} requires at least two incoming branches")
        resolved_incoming = []
        aliases = []
        for endpoint in incoming:
            resolved = _qualified(endpoint.get("namespace"), endpoint.get("node"))
            alias = endpoint.get("alias")
            if alias:
                aliases.append(alias)
            resolved_incoming.append({"node": resolved, "alias": alias, "source": endpoint})
        if len(aliases) != len(set(aliases)):
            raise FlowReuseCompileError(f"join {qid} incoming aliases must be unique")
        target = join.get("target") or {}
        resolved_target = _qualified(target.get("namespace"), target.get("node"))
        synthetic_node = f"{qid}.__join__"
        ops.append({
            "op": "FLOW.JOIN.DEF",
            "id": qid,
            "source_local_id": jid,
            "namespace": ns,
            "incoming": resolved_incoming,
            "target": resolved_target,
            "state_contract": join.get("state_contract"),
            "merge_policy": join.get("merge_policy"),
            "conflict_policy": join.get("conflict_policy"),
            "resolver_ref": join.get("resolver_ref"),
            "provenance_policy": join.get("provenance_policy", "preserve_all_inputs"),
            "lowered_node": synthetic_node,
        })
        ops.append({
            "op": "NODE.DEF",
            "id": synthetic_node,
            "source_local_id": jid,
            "synthetic": True,
            "synthetic_kind": "flow_join",
            "exposed_by_cli": False,
        })
        for endpoint in resolved_incoming:
            ops.append({
                "op": "FLOW.EDGE",
                "id": f"{qid}.edge.in.{endpoint['alias'] or endpoint['node']}",
                "from": endpoint["node"],
                "to": synthetic_node,
                "edge_kind": "join_incoming",
                "join_id": qid,
                "source_provenance": endpoint["source"],
            })
        ops.append({
            "op": "FLOW.EDGE",
            "id": f"{qid}.edge.out",
            "from": synthetic_node,
            "to": resolved_target,
            "edge_kind": "join_target",
            "join_id": qid,
        })

    for ref in refs:
        rid, ns = ref.get("id"), ref.get("namespace")
        qid = _qualified(ns, rid)
        if qid in seen:
            raise FlowReuseCompileError(f"duplicate flow reuse id: {qid}")
        seen.add(qid)
        tail_ns = ref.get("tail_namespace") or ns
        tail_id = ref.get("tail_id")
        tail = tail_index.get((tail_ns, tail_id))
        if tail is None:
            raise FlowReuseCompileError(f"reference {qid} targets missing shared tail {tail_ns}.{tail_id}")
        if ref.get("entry") != tail.get("entry"):
            raise FlowReuseCompileError(f"reference {qid} entry does not match shared tail entry")
        policy = ref.get("namespace_policy")
        ns_map = ref.get("namespace_map") or {}
        if policy == "explicit_map":
            if not ns_map or ns not in ns_map or ns_map[ns] != tail_ns:
                raise FlowReuseCompileError(f"reference {qid} requires complete explicit namespace map")
            _validate_one_to_one(ns_map, f"reference {qid} namespace_map")
        elif policy == "inherit" and tail_ns != ns:
            raise FlowReuseCompileError(f"reference {qid} cannot inherit across namespaces")
        elif policy not in {"inherit", "qualified", "explicit_map"}:
            raise FlowReuseCompileError(f"reference {qid} has unsupported namespace policy")
        for direction in ("import_state", "export_state"):
            rename = (ref.get(direction) or {}).get("rename") or {}
            _validate_one_to_one(rename, f"reference {qid} {direction}.rename")
        return_to = ref.get("return_to")
        if not isinstance(return_to, str) or not return_to:
            raise FlowReuseCompileError(f"reference {qid} requires deterministic return_to")
        max_call_depth = ref.get("max_call_depth", 16)
        if not isinstance(max_call_depth, int) or isinstance(max_call_depth, bool) or not 1 <= max_call_depth <= 128:
            raise FlowReuseCompileError(f"reference {qid} max_call_depth must be an integer from 1 to 128")
        resolved_entry = _qualified(tail_ns, tail["entry"])
        resolved_nodes = [_qualified(tail_ns, n) for n in tail.get("nodes", [])]
        ops.append({
            "op": "SHARED.TAIL.REFERENCE.RESOLVED",
            "id": qid,
            "source_local_id": rid,
            "namespace": ns,
            "tail_id": _qualified(tail_ns, tail_id),
            "resolved_entry": resolved_entry,
            "resolved_nodes": resolved_nodes,
            "return_to": return_to,
            "max_call_depth": max_call_depth,
            "namespace_policy": policy,
            "namespace_map": ns_map,
            "import_state": ref.get("import_state", {}),
            "export_state": ref.get("export_state", {}),
            "protected_fields": ref.get("protected_fields", []),
            "preserve_provenance": ref.get("preserve_provenance", True),
            "source_provenance": {"reference": ref, "tail": tail},
        })
        ops.append({
            "op": "FLOW.EDGE",
            "id": f"{qid}.edge.reference",
            "from": qid,
            "to": resolved_entry,
            "edge_kind": "shared_tail_reference",
            "reference_id": qid,
        })

    return ops


def compile_source(source: dict[str, Any]) -> dict[str, Any]:
    meta = source.get("ordo") or {}
    package = meta.get("package", "unnamed.package")
    ops: list[dict[str, Any]] = []

    graph_contract = source.get("graph_contract")
    if graph_contract:
        ops.append({
            "op": "GRAPH.CONTRACT",
            "id": namespace_id(package, "graph_contract"),
            **graph_contract,
        })

    ops.append({
        "op": "PROGRAM.DEF",
        "id": package,
        "ordo_version": meta.get("version"),
        "control_level": meta.get("control_level"),
        "execution_mode": meta.get("execution_mode"),
    })

    for include in source.get("includes", []) or []:
        ops.append({
            "op": "LIB.INCLUDE",
            "id": namespace_id(package, f"include.{include.get('library')}"),
            "library": include.get("library"),
            "version": include.get("version"),
            "alias": include.get("as"),
        })

    interaction_model = source.get("interaction_model")
    if interaction_model:
        ops.append({
            "op": "INTERACTION.MODEL",
            "id": namespace_id(package, "interaction_model"),
            **interaction_model,
        })

    process_rail = source.get("process_rail")
    if process_rail:
        ops.append({
            "op": "PROCESS_RAIL.DEF",
            "id": namespace_id(package, process_rail.get("rail_id", "process_rail")),
            **process_rail,
        })

    conversation_semantics = source.get("conversation_semantics")
    if conversation_semantics:
        ops.append({
            "op": "CONVERSATION.SEMANTICS",
            "id": namespace_id(package, "conversation_semantics"),
            **conversation_semantics,
        })

    conversation_scope_guard = source.get("conversation_scope_guard")
    if conversation_scope_guard:
        ops.append({
            "op": "CONVERSATION.SCOPE.DEF",
            "id": namespace_id(package, conversation_scope_guard.get("id", "conversation_scope_guard")),
            "source_local_id": conversation_scope_guard.get("id", "conversation_scope_guard"),
            "supported": conversation_scope_guard.get("supported", False),
            "enabled": conversation_scope_guard.get("enabled", False),
            "mode": conversation_scope_guard.get("mode"),
            "scope": conversation_scope_guard.get("scope"),
            "out_of_scope_behavior": conversation_scope_guard.get("out_of_scope_behavior"),
            "state_change_on_out_of_scope": conversation_scope_guard.get("state_change_on_out_of_scope", False),
            "escalation": conversation_scope_guard.get("escalation", {}),
            "trace": conversation_scope_guard.get("trace", {}),
        })

    hybrid_execution = source.get("hybrid_execution")
    if hybrid_execution:
        ops.append({
            "op": "HYBRID_EXECUTION.MODEL",
            "id": namespace_id(package, "hybrid_execution"),
            **hybrid_execution,
        })

    intent = source.get("intent")
    if intent:
        ops.append({
            "op": "INTENT.DEF",
            "id": namespace_id(package, intent.get("id", "INTENT")),
            "description": intent.get("description"),
        })

    contract = source.get("contract")
    if contract:
        ops.append({
            "op": "CONTRACT.DEF",
            "id": namespace_id(package, contract.get("id", "CONTRACT")),
            "required": contract.get("required", []),
        })

    state = source.get("state")
    if state:
        ops.append({
            "op": "STATE.SCHEMA",
            "id": namespace_id(package, state.get("id", "STATE")),
            "schema": state.get("schema", {}),
        })

    execution_trace = source.get("execution_trace")
    if execution_trace:
        from .execution_trace import normalize_policy
        trace_policy = normalize_policy(execution_trace)
        ops.append({
            "op": "EXECUTION_TRACE.DEF",
            "id": namespace_id(package, execution_trace.get("id", "EXECUTION_TRACE")),
            "source_local_id": execution_trace.get("id", "EXECUTION_TRACE"),
            **trace_policy,
        })

    ops.extend(lower_flow_reuse(source, package))

    for node in source.get("nodes", []) or []:
        ops.append({
            "op": "NODE.DEF",
            "id": namespace_id(package, node["id"]),
            "source_local_id": node["id"],
            "question": node.get("question"),
            "answer_type": node.get("answer_type"),
            "on_answer": node.get("on_answer"),
            "on_unmatched_input": node.get("on_unmatched_input"),
            "allow_unmatched_input": node.get("allow_unmatched_input", False),
            "antipattern_hooks": node.get("antipattern_hooks"),
            "allowed_from": node.get("allowed_from") or node.get("incoming_from") or [],
            "entry_modes": node.get("entry_modes") or [],
            "node_context": node.get("node_context") or {},
        })
        if node.get("on_unmatched_input"):
            ops.append({
                "op": "CLARIFY.REQUEST",
                "id": namespace_id(package, f"{node['id']}.on_unmatched_input"),
                "source_node": namespace_id(package, node["id"]),
                **node["on_unmatched_input"],
            })


    canary_secret = f"canary-{secrets.token_hex(16)}"
    canary_id = namespace_id(package, "N99_CANARY_DO_NOT_EMIT")
    ops.append({
        "op": "NODE.DEF",
        "id": canary_id,
        "source_local_id": "N99_CANARY_DO_NOT_EMIT",
        "question": canary_secret,
        "answer_type": "canary_never_emit",
        "on_answer": {},
        "on_unmatched_input": {},
        "allow_unmatched_input": False,
        "canary": True,
        "exposed_by_cli": False,
        "note": "M59.3 canary node: never returned by runtime CLI; leak proves raw IR exposure.",
    })

    for gate in source.get("gates", []) or []:
        ops.append({
            "op": "GATE.DEF",
            "id": namespace_id(package, gate["id"]),
            "source_local_id": gate["id"],
            "method": gate.get("method"),
            "trust_class": gate.get("trust_class"),
            "condition": gate.get("condition"),
            "on_fail": gate.get("on_fail"),
        })

    for assertion in source.get("assertions", []) or []:
        assertion_id = namespace_id(package, assertion["id"])
        ops.append({
            "op": "ASSERTION.DEF",
            "id": assertion_id,
            "source_local_id": assertion["id"],
            "polarity": assertion.get("polarity"),
            "condition": assertion.get("condition"),
            "phase": assertion.get("phase"),
            "severity": assertion.get("severity"),
            "on_fail": assertion.get("on_fail"),
        })
        phases = assertion.get("phase") or []
        if "runtime" in phases:
            ops.append({
                "op": "ASSERTION.PROJECT",
                "id": f"{assertion_id}.runtime_projection",
                "source_assertion": assertion_id,
                "target": "ASSERT.NOT" if assertion.get("polarity") == "not" else "ASSERT.MUST",
            })
        if "test" in phases:
            ops.append({
                "op": "ASSERTION.PROJECT",
                "id": f"{assertion_id}.test_projection",
                "source_assertion": assertion_id,
                "target": "EXPECT.NOT" if assertion.get("polarity") == "not" else "EXPECT.MUST",
            })


    for contract_obj in source.get("contracts", []) or []:
        ops.append({
            "op": "CONTRACT.INSTANCE",
            "id": namespace_id(package, contract_obj["id"]),
            **contract_obj,
        })

    for artifact in source.get("artifacts", []) or []:
        ops.append({
            "op": "ARTIFACT.DEF",
            "id": namespace_id(package, artifact["id"]),
            **artifact,
        })

    for requirement in source.get("artifact_requirements", []) or []:
        ops.append({
            "op": "ARTIFACT.REQUIREMENT",
            "id": namespace_id(package, requirement["id"]),
            **requirement,
        })

    for rule in source.get("coverage_rules", []) or []:
        ops.append({
            "op": "COVERAGE.RULE",
            "id": namespace_id(package, rule["id"]),
            **rule,
        })

    for assertion in source.get("rendered_artifact_assertions", []) or []:
        ops.append({
            "op": "RENDERED_ARTIFACT.ASSERT",
            "id": namespace_id(package, assertion["id"]),
            **assertion,
        })

    if source.get("go_no_go"):
        ops.append({
            "op": "GO_NO_GO.DECISION",
            "id": namespace_id(package, "go_no_go"),
            **source["go_no_go"],
        })

    for output in source.get("outputs", []) or []:
        ops.append({
            "op": "OUTPUT.DEF",
            "id": namespace_id(package, output["id"]),
            "source_local_id": output["id"],
            "type": output.get("type"),
            "allowed_after": [namespace_id(package, g) for g in output.get("allowed_after", [])],
        })

    for block in source.get("freeform", []) or []:
        ops.append({
            "op": "FREEFORM.DEF",
            "id": namespace_id(package, block["id"]),
            "source_local_id": block["id"],
            "role": block.get("role"),
            "maturity": block.get("maturity"),
            "incident_count": block.get("incident_count", 0),
            "incident_threshold": block.get("incident_threshold", 3),
        })

    return {
        "ordo_version": meta.get("version"),
        "package": package,
        "compiled_at": datetime.now(timezone.utc).isoformat(),
        "ir_format": "semantic_json_ir",
        "security": {
            "trust_layer": "m59_3_canary",
            "canary_node_id": canary_id,
            "canary_secret": canary_secret,
            "canary_policy": "Never emitted by runtime CLI; verify-session scans runtime-visible outputs for leaks.",
        },
        "ops": ops,
    }
