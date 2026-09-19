"""Authoring diagnostics for single-responsibility node decomposition.

The analyser never rewrites a graph.  It makes the complete preservation
surface explicit before an author splits a node into smaller responsibilities.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from .graph_topology import graph_topology
from .state_lineage import validate_state_lineage


RESPONSIBILITIES = ("collection", "analysis", "drafting", "confirmation", "routing", "technical")
PASSING = {"passed", "not_enabled"}


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _state_writes(node: dict[str, Any]) -> list[str]:
    writes = {str(item) for item in (node.get("writes") or []) if isinstance(item, str)}
    for item in _walk(node.get("on_answer") or {}):
        update = item.get("update_state") if isinstance(item, dict) else None
        if isinstance(update, dict):
            writes.update(str(path) for path in update)
    return sorted(writes)


def _state_reads(node: dict[str, Any]) -> list[str]:
    reads: set[str] = set()
    for key in ("reads", "inputs", "required_fields"):
        reads.update(str(item) for item in (node.get(key) or []) if isinstance(item, str))
    return sorted(reads)


def classify_responsibilities(node: dict[str, Any], *, outgoing_count: int = 0) -> list[str]:
    """Classify declared/observable responsibility types without text guessing."""
    explicit = node.get("responsibility_kinds")
    if isinstance(explicit, list):
        return [kind for kind in RESPONSIBILITIES if kind in explicit]
    text = " ".join(str(node.get(key) or "") for key in ("id", "kind", "node_type", "responsibility_id")).casefold()
    kinds: set[str] = set()
    if node.get("question") or node.get("inputs") or node.get("required_fields"):
        kinds.add("collection")
    if any(token in text for token in ("analysis", "derive", "compare", "classif", "assess", "evaluate")) or node.get("analysis") is not None:
        kinds.add("analysis")
    if any(token in text for token in ("draft", "materializ", "render", "generate", "artifact")) or node.get("template") is not None or node.get("outputs"):
        kinds.add("drafting")
    if any(token in text for token in ("confirm", "approve", "review", "signoff")) or node.get("requires_confirmation") is True:
        kinds.add("confirmation")
    # A single normal successor is ordinary progression.  Routing becomes a
    # separate responsibility only where the node selects among routes.
    if outgoing_count > 1 or node.get("conditional_routes") or node.get("route_context"):
        kinds.add("routing")
    if node.get("processing") or node.get("internal_prompt") or node.get("tool") or node.get("executor"):
        kinds.add("technical")
    return [kind for kind in RESPONSIBILITIES if kind in kinds]


def _lineage_index(source: dict[str, Any]) -> dict[str, dict[str, Any]]:
    report = validate_state_lineage(source)
    return {str(item.get("path")): item for item in (report.get("fields") or []) if isinstance(item, dict) and item.get("path")}


def _cycle_components(adjacency: dict[str, list[str]]) -> list[list[str]]:
    """Return only cyclic SCCs using iterative forward/reverse reachability."""
    components: list[list[str]] = []
    reverse: dict[str, list[str]] = {node: [] for node in adjacency}
    for origin, targets in adjacency.items():
        for target in targets:
            if target in reverse:
                reverse[target].append(origin)

    def reachable(start: str, edges: dict[str, list[str]]) -> set[str]:
        seen = {start}
        stack = list(edges.get(start) or [])
        while stack:
            current = stack.pop()
            if current in seen or current not in edges:
                continue
            seen.add(current)
            stack.extend(edges.get(current) or [])
        return seen

    for start in sorted(adjacency):
        component = sorted(reachable(start, adjacency) & reachable(start, reverse))
        is_self_cycle = start in (adjacency.get(start) or [])
        if len(component) > 1 or is_self_cycle:
            if component not in components:
                components.append(component)
    return sorted(components)


def inspect_node_split(source: dict[str, Any], node_id: str, *, replacement_ids: list[str] | None = None) -> dict[str, Any]:
    """Report everything a manual split must preserve; source remains unchanged."""
    topology = graph_topology(source)
    node = topology["nodes"].get(node_id)
    if node is None:
        return {"status": "failed", "node": node_id, "issues": [{"severity": "error", "code": "NODE_SPLIT_NODE_MISSING", "message": "node does not exist.", "location": "nodes"}]}
    adjacency: dict[str, list[str]] = topology["adjacency"]
    incoming = sorted(source_id for source_id, targets in adjacency.items() if node_id in targets)
    outgoing = sorted(adjacency.get(node_id) or [])
    gates = set(topology["gates"])
    touched_gates = sorted(set(incoming + outgoing) & gates)
    lineage = _lineage_index(source)
    writes = _state_writes(node)
    reads = _state_reads(node)
    owned = sorted(path for path, item in lineage.items() if item.get("owner") == node_id)
    consumed = sorted(path for path, item in lineage.items() if node_id in (item.get("consumers") or []))
    replacements = [item for item in (replacement_ids or []) if isinstance(item, str) and item]
    known = set(topology["by_id"])
    issues: list[dict[str, Any]] = []
    if replacements and len(replacements) != len(set(replacements)):
        issues.append({"severity": "error", "code": "NODE_SPLIT_REPLACEMENT_DUPLICATE", "message": "replacement ids must be unique.", "location": "replacement_ids"})
    collisions = sorted(set(replacements) & known)
    if collisions:
        issues.append({"severity": "error", "code": "NODE_SPLIT_REPLACEMENT_EXISTS", "message": "replacement ids must not collide with active graph ids.", "location": "replacement_ids", "ids": collisions})
    return {
        "schema_version": "ordo.node_split_impact.v1",
        "status": "passed" if not issues else "failed",
        "node": node_id,
        "responsibilities": classify_responsibilities(node, outgoing_count=len(outgoing)),
        "preservation_surface": {
            "incoming_edges": incoming,
            "outgoing_edges": outgoing,
            "gate_bindings": touched_gates,
            "cycle_components": [component for component in _cycle_components(adjacency) if node_id in component],
            "state_writes": writes,
            "state_reads": reads,
            "state_lineage_owner_paths": owned,
            "state_lineage_consumer_paths": consumed,
        },
        "replacement_ids": replacements,
        "required_split_actions": {
            "incoming_edges": "Retarget every incoming edge to the first replacement node.",
            "outgoing_edges": "Reattach every outgoing edge from the final replacement node.",
            "state_ownership": "Assign each owned state path to exactly one replacement node and preserve all declared consumers.",
            "gate_bindings": "Preserve each listed gate binding and reevaluate cycle declarations after rewiring.",
            "cycles": "Keep every declared cycle region valid, or explicitly replace it with an equivalent declared region.",
        },
        "issues": issues,
        "source_mutated": False,
    }


def validate_node_responsibilities(source: dict[str, Any]) -> dict[str, Any]:
    """Detect compound authoring responsibilities under an optional policy."""
    policy = source.get("node_responsibility_policy") or {}
    mode = policy.get("mode", "advisory") if isinstance(policy, dict) else "advisory"
    topology = graph_topology(source)
    findings: list[dict[str, Any]] = []
    for node_id, node in sorted(topology["nodes"].items()):
        kinds = classify_responsibilities(node, outgoing_count=len(topology["adjacency"].get(node_id) or []))
        if len(kinds) <= 1:
            continue
        severity = "error" if mode == "strict" else "warning"
        findings.append({
            "severity": severity,
            "code": "NODE_RESPONSIBILITY_COMPOUND",
            "message": "Node combines multiple responsibilities; split it before authoring continues.",
            "location": f"nodes[{node_id}]",
            "node": node_id,
            "responsibilities": kinds,
            "split_preview": inspect_node_split(source, node_id),
        })
    errors = [item for item in findings if item["severity"] == "error"]
    return {
        "schema_version": "ordo.node_responsibility.v1",
        "status": "failed" if errors else "passed",
        "mode": mode,
        "summary": {"nodes": len(topology["nodes"]), "compound_nodes": len(findings), "errors": len(errors), "warnings": len(findings) - len(errors)},
        "issues": findings,
    }
