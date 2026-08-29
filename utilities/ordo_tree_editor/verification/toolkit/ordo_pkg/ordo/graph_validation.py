from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from .graph_topology import graph_topology


@dataclass
class GraphIssue:
    severity: str
    code: str
    message: str
    location: str
    path: list[str] | None = None


def _target_declarations(value: Any, path: str = "root", scope: str = "root") -> list[tuple[str, str, str]]:
    """Return target, location, and declaration-scope triples.

    A target repeated in one list/scope is a duplicate declaration. Targets
    converging from different answer branches intentionally remain distinct
    declarations and are valid graph edges.
    """
    out: list[tuple[str, str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key == "next" and isinstance(child, str):
                out.append((child, child_path, scope))
            else:
                out.extend(_target_declarations(child, child_path, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            out.extend(_target_declarations(child, f"{path}[{index}]", scope))
    return out


def _deprecated(node: dict[str, Any]) -> bool:
    return str(node.get("lifecycle_status", "")).startswith("deprecated") or node.get("active_runtime_node") is False


def _tarjan(nodes: set[str], adj: dict[str, list[str]]) -> list[list[str]]:
    """Return SCCs using an iterative Kosaraju traversal.

    The historical recursive implementation could hit Python's recursion
    limit on large but valid process graphs.  Both passes below use explicit
    stacks and keep memory O(V + E).
    """
    ordered_nodes = sorted(nodes)
    visited: set[str] = set()
    finish: list[str] = []

    for root in ordered_nodes:
        if root in visited:
            continue
        visited.add(root)
        stack: list[tuple[str, int]] = [(root, 0)]
        while stack:
            current, index = stack[-1]
            neighbours = [n for n in adj.get(current, []) if n in nodes]
            if index < len(neighbours):
                nxt = neighbours[index]
                stack[-1] = (current, index + 1)
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append((nxt, 0))
            else:
                finish.append(current)
                stack.pop()

    reverse: dict[str, list[str]] = {node: [] for node in nodes}
    for source in nodes:
        for target in adj.get(source, []):
            if target in nodes:
                reverse[target].append(source)

    assigned: set[str] = set()
    result: list[list[str]] = []
    for root in reversed(finish):
        if root in assigned:
            continue
        component: list[str] = []
        stack = [root]
        assigned.add(root)
        while stack:
            current = stack.pop()
            component.append(current)
            for nxt in reverse.get(current, []):
                if nxt not in assigned:
                    assigned.add(nxt)
                    stack.append(nxt)
        result.append(component)
    return result


def validate_process_graph(source: dict[str, Any]) -> dict[str, Any]:
    issues: list[GraphIssue] = []
    topology = graph_topology(source)
    node_by_id: dict[str, dict[str, Any]] = topology["nodes"]
    gate_by_id: dict[str, dict[str, Any]] = topology["gates"]
    by_id: dict[str, dict[str, Any]] = topology["by_id"]
    adj: dict[str, list[str]] = topology["adjacency"]
    gate_ids: set[str] = set(topology["executable_gate_ids"])
    node_ids = set(node_by_id)
    ids = set(by_id)
    contract = source.get("graph_contract") or {}
    entry = topology["entry"]
    external_terminals = set(contract.get("external_terminal_targets", []) or [])
    dynamic_terminal_sources = set(contract.get("dynamic_terminal_sources", []) or [])
    allowed_regions = contract.get("allowed_cycle_regions", []) or []
    allowed_sets = [set(r.get("nodes", []) or []) for r in allowed_regions if isinstance(r, dict)]

    for duplicate_id in sorted(topology["duplicate_ids"]):
        issues.append(GraphIssue(
            "error",
            "GRAPH_ID_DUPLICATE",
            f"Graph ID {duplicate_id!r} is declared as both node and gate.",
            "nodes/gates",
            [duplicate_id],
        ))

    # BL-ORDO-065: validate the explicit incoming-edge contract before
    # topology checks. The source tree is authoritative; compiler lowering
    # must not silently infer or repair asymmetric declarations.
    incoming_contract_enabled = (
        contract.get("bidirectional_transition_policy") == "explicit_source_and_target"
        or any("allowed_from" in vertex or "incoming_from" in vertex for vertex in by_id.values())
    )
    incoming_by_target: dict[str, list[str]] = {vertex_id: [] for vertex_id in ids}
    for vertex_id, vertex in by_id.items():
        if not incoming_contract_enabled:
            continue
        kind = "gate" if vertex_id in gate_ids else "node"
        raw_incoming = vertex.get("allowed_from")
        if raw_incoming is None:
            raw_incoming = vertex.get("incoming_from")
        if raw_incoming is None:
            if not _deprecated(vertex):
                issues.append(GraphIssue("error", "GRAPH_INCOMING_REQUIRED", f"Active {kind} must declare allowed_from.", f"{kind}s[{vertex_id}].allowed_from", [vertex_id]))
            raw_incoming = []
        if not isinstance(raw_incoming, list) or not all(isinstance(incoming_source, str) for incoming_source in raw_incoming):
            issues.append(GraphIssue("error", "GRAPH_INCOMING_INVALID", "allowed_from must be a list of graph vertex IDs.", f"{kind}s[{vertex_id}].allowed_from", [vertex_id]))
            raw_incoming = []
        if len(raw_incoming) != len(set(raw_incoming)):
            issues.append(GraphIssue("error", "GRAPH_INCOMING_DUPLICATE", "allowed_from must not contain duplicate source IDs.", f"{kind}s[{vertex_id}].allowed_from", [vertex_id]))
        for incoming_source in raw_incoming:
            if incoming_source not in ids:
                issues.append(GraphIssue("error", "GRAPH_SOURCE_MISSING", f"Incoming source {incoming_source!r} does not exist.", f"{kind}s[{vertex_id}].allowed_from", [incoming_source, vertex_id]))
            else:
                incoming_by_target[vertex_id].append(incoming_source)
                if vertex_id not in adj.get(incoming_source, []):
                    issues.append(GraphIssue("error", "GRAPH_EDGE_ASYMMETRIC", f"Vertex {incoming_source} allows no transition to {vertex_id}, but {vertex_id}.allowed_from declares it.", f"{kind}s[{vertex_id}].allowed_from", [incoming_source, vertex_id]))

    if incoming_contract_enabled:
        for source_id, targets in adj.items():
            source_kind = "gate" if source_id in gate_ids else "node"
            declarations = (
                _target_declarations(node_by_id[source_id].get("on_answer", {}), f"nodes[{source_id}].on_answer")
                if source_id in node_ids
                else [(target, f"gates[{source_id}].transition", target) for target in targets]
            )
            seen_by_scope: dict[tuple[str, str], str] = {}
            for target, location, scope in declarations:
                key = (scope, target)
                if key in seen_by_scope:
                    issues.append(GraphIssue("error", "GRAPH_TRANSITION_DUPLICATE", f"Transition to {target!r} is declared more than once in the same transition scope.", location, [source_id, target]))
                seen_by_scope[key] = location
                if target in ids and source_id not in incoming_by_target.get(target, []):
                    issues.append(GraphIssue("error", "GRAPH_EDGE_ASYMMETRIC", f"Transition {source_id} -> {target} is not mirrored by {target}.allowed_from.", location, [source_id, target]))

    if not entry or entry not in ids:
        issues.append(GraphIssue("error", "GRAPH_ENTRY_INVALID", "graph_contract.entry_node must reference an existing node or executable gate.", "graph_contract.entry_node"))

    for vertex_id in sorted(dynamic_terminal_sources - ids):
        issues.append(GraphIssue("error", "GRAPH_DYNAMIC_TERMINAL_SOURCE_MISSING", f"Dynamic terminal source {vertex_id!r} does not reference an existing graph vertex.", "graph_contract.dynamic_terminal_sources", [vertex_id]))

    for vertex_id, targets in adj.items():
        kind = "gate" if vertex_id in gate_ids else "node"
        for target in targets:
            if target not in ids and target not in external_terminals:
                issues.append(GraphIssue("error", "GRAPH_TARGET_MISSING", f"Transition target {target!r} does not exist and is not declared as an external terminal target.", f"{kind}s[{vertex_id}].transition", [vertex_id, target]))
        if by_id[vertex_id].get("terminal") is True and targets:
            issues.append(GraphIssue("error", "GRAPH_TERMINAL_OUTGOING", f"Terminal {kind} {vertex_id} must not declare outgoing transitions.", f"{kind}s[{vertex_id}].transition", [vertex_id, *targets]))

    active_ids = {vertex_id for vertex_id, vertex in by_id.items() if not _deprecated(vertex)}
    for vertex_id in sorted(active_ids):
        if incoming_contract_enabled and vertex_id != entry and not incoming_by_target.get(vertex_id):
            kind = "gate" if vertex_id in gate_ids else "node"
            code = "GRAPH_VERTEX_NO_INCOMING" if kind == "gate" else "GRAPH_NODE_NO_INCOMING"
            issues.append(GraphIssue("error", code, f"Active non-entry {kind} {vertex_id} has no declared incoming edge.", f"{kind}s[{vertex_id}].allowed_from", [vertex_id]))
    reachable: set[str] = set()
    if entry in ids:
        stack = [entry]
        while stack:
            current = stack.pop()
            if current in reachable:
                continue
            reachable.add(current)
            stack.extend(t for t in adj.get(current, []) if t in ids)
    for vertex_id in sorted(active_ids - reachable):
        kind = "gate" if vertex_id in gate_ids else "node"
        code = "GRAPH_VERTEX_UNREACHABLE" if kind == "gate" else "GRAPH_NODE_UNREACHABLE"
        issues.append(GraphIssue("error", code, f"Active {kind} {vertex_id} is unreachable from entry vertex {entry}.", f"{kind}s[{vertex_id}]", [entry, vertex_id] if entry else [vertex_id]))

    for vertex_id in sorted(active_ids):
        vertex = by_id[vertex_id]
        if not adj.get(vertex_id) and vertex.get("terminal") is not True:
            kind = "gate" if vertex_id in gate_ids else "node"
            code = "GRAPH_DEAD_END_VERTEX" if kind == "gate" else "GRAPH_DEAD_END_NODE"
            issues.append(GraphIssue("error", code, f"Active {kind} {vertex_id} has no outgoing transition and is not terminal.", f"{kind}s[{vertex_id}]", [vertex_id]))

    terminal_vertices = {vertex_id for vertex_id, vertex in by_id.items() if vertex.get("terminal") is True}
    # A dynamic decision node may terminate through a runtime-selected outcome
    # that cannot be represented as one static `next` edge.  Such nodes must
    # be declared explicitly in the contract; this does not permit terminal
    # nodes to have outgoing edges.
    can_terminate = set(terminal_vertices) | (dynamic_terminal_sources & ids)
    changed = True
    while changed:
        changed = False
        for vertex_id in active_ids:
            targets = adj.get(vertex_id, [])
            if vertex_id not in can_terminate and any(t in can_terminate or t in external_terminals for t in targets):
                can_terminate.add(vertex_id)
                changed = True
    for vertex_id in sorted((active_ids & reachable) - can_terminate):
        kind = "gate" if vertex_id in gate_ids else "node"
        issues.append(GraphIssue("error", "GRAPH_NO_TERMINAL_PATH", f"Reachable active {kind} {vertex_id} cannot reach a terminal outcome.", f"{kind}s[{vertex_id}]", [vertex_id]))

    components = _tarjan(active_ids, adj)
    cycle_components = [c for c in components if len(c) > 1 or (len(c) == 1 and c[0] in adj.get(c[0], []))]
    for component in cycle_components:
        comp = set(component)
        if not any(comp <= allowed for allowed in allowed_sets):
            issues.append(GraphIssue("error", "GRAPH_CYCLE_UNDECLARED", "Cycle detected outside graph_contract.allowed_cycle_regions.", "graph_contract.allowed_cycle_regions", sorted(component)))


    from .transition_provenance import validate_transition_provenance
    provenance_report = validate_transition_provenance(source)
    for item in provenance_report.get("issues", []):
        issues.append(GraphIssue(
            item.get("severity", "error"),
            item.get("code", "GRAPH_TRANSITION_PROVENANCE"),
            item.get("message", "Transition provenance defect."),
            item.get("location", "graph_contract.transition_provenance"),
            [x for x in [item.get("source_node"), item.get("target_node")] if x],
        ))

    errors = [asdict(i) for i in issues if i.severity == "error"]
    warnings = [asdict(i) for i in issues if i.severity == "warning"]
    return {
        "status": "passed" if not errors else "failed",
        "summary": {
            "nodes": len(node_ids),
            "gates": len(gate_by_id),
            "graph_vertices": len(ids),
            "active_vertices": len(active_ids),
            "reachable_active_vertices": len(active_ids & reachable),
            "terminal_vertices": len(terminal_vertices),
            "active_nodes": len(active_ids & node_ids),
            "reachable_active_nodes": len(active_ids & reachable & node_ids),
            "terminal_nodes": len(terminal_vertices & node_ids),
            "external_terminal_targets": len(external_terminals),
            "dynamic_terminal_sources": len(dynamic_terminal_sources & ids),
            "cycles_detected": len(cycle_components),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "issues": [asdict(i) for i in issues],
        "cycle_components": [sorted(c) for c in cycle_components],
        "transition_provenance": provenance_report,
    }
