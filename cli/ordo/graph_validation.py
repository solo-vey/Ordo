from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class GraphIssue:
    severity: str
    code: str
    message: str
    location: str
    path: list[str] | None = None


def _targets(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "next" and isinstance(child, str):
                out.append(child)
            else:
                out.extend(_targets(child))
    elif isinstance(value, list):
        for child in value:
            out.extend(_targets(child))
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
    nodes_list = source.get("nodes", []) or []
    by_id = {n.get("id"): n for n in nodes_list if isinstance(n, dict) and n.get("id")}
    ids = set(by_id)
    contract = source.get("graph_contract") or {}
    entry = contract.get("entry_node") or (nodes_list[0].get("id") if nodes_list else None)
    external_terminals = set(contract.get("external_terminal_targets", []) or [])
    allowed_regions = contract.get("allowed_cycle_regions", []) or []
    allowed_sets = [set(r.get("nodes", []) or []) for r in allowed_regions if isinstance(r, dict)]

    adj = {node_id: _targets(node) for node_id, node in by_id.items()}

    if not entry or entry not in ids:
        issues.append(GraphIssue("error", "GRAPH_ENTRY_INVALID", "graph_contract.entry_node must reference an existing node.", "graph_contract.entry_node"))

    for node_id, targets in adj.items():
        for target in targets:
            if target not in ids and target not in external_terminals:
                issues.append(GraphIssue("error", "GRAPH_TARGET_MISSING", f"Transition target {target!r} does not exist and is not declared as an external terminal target.", f"nodes[{node_id}].transition", [node_id, target]))

    active_ids = {node_id for node_id, node in by_id.items() if not _deprecated(node)}
    reachable: set[str] = set()
    if entry in ids:
        stack = [entry]
        while stack:
            current = stack.pop()
            if current in reachable:
                continue
            reachable.add(current)
            stack.extend(t for t in adj.get(current, []) if t in ids)
    for node_id in sorted(active_ids - reachable):
        issues.append(GraphIssue("error", "GRAPH_NODE_UNREACHABLE", f"Active node {node_id} is unreachable from entry node {entry}.", f"nodes[{node_id}]", [entry, node_id] if entry else [node_id]))

    for node_id in sorted(active_ids):
        node = by_id[node_id]
        if not adj.get(node_id) and node.get("terminal") is not True:
            issues.append(GraphIssue("error", "GRAPH_DEAD_END_NODE", f"Active node {node_id} has no outgoing transition and is not terminal.", f"nodes[{node_id}]", [node_id]))

    terminal_nodes = {node_id for node_id, node in by_id.items() if node.get("terminal") is True}
    can_terminate = set(terminal_nodes)
    changed = True
    while changed:
        changed = False
        for node_id in active_ids:
            targets = adj.get(node_id, [])
            if node_id not in can_terminate and any(t in can_terminate or t in external_terminals for t in targets):
                can_terminate.add(node_id)
                changed = True
    for node_id in sorted((active_ids & reachable) - can_terminate):
        issues.append(GraphIssue("error", "GRAPH_NO_TERMINAL_PATH", f"Reachable active node {node_id} cannot reach a terminal outcome.", f"nodes[{node_id}]", [node_id]))

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
            "nodes": len(ids),
            "active_nodes": len(active_ids),
            "reachable_active_nodes": len(active_ids & reachable),
            "terminal_nodes": len(terminal_nodes),
            "external_terminal_targets": len(external_terminals),
            "cycles_detected": len(cycle_components),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "issues": [asdict(i) for i in issues],
        "cycle_components": [sorted(c) for c in cycle_components],
        "transition_provenance": provenance_report,
    }
