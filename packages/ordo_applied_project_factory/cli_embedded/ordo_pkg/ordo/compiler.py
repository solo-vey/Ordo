from __future__ import annotations

from typing import Any
from datetime import datetime, timezone
import secrets


def namespace_id(package: str, local_id: str) -> str:
    if "." in local_id and local_id.startswith(package + "."):
        return local_id
    return f"{package}.{local_id}"


def compile_source(source: dict[str, Any]) -> dict[str, Any]:
    meta = source.get("ordo") or {}
    package = meta.get("package", "unnamed.package")
    ops: list[dict[str, Any]] = []

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
