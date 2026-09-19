"""Deterministic pseudo-chat materialization and graph-backed documentation checks."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .graph_topology import graph_topology


NODE_MARKER = re.compile(r"<!--\s*ordo-node:\s*([^\s>]+)\s*-->")
EDGE_MARKER = re.compile(r"<!--\s*ordo-transition:\s*([^\s>-]+)\s*->\s*([^\s>]+)\s*-->")


def _reachable(topology: dict[str, Any]) -> set[str]:
    entry = topology.get("entry")
    adjacency = topology.get("adjacency") or {}
    seen: set[str] = set()
    stack = [entry] if isinstance(entry, str) else []
    while stack:
        current = stack.pop()
        if current in seen or current not in adjacency:
            continue
        seen.add(current)
        stack.extend(adjacency.get(current) or [])
    return seen


def _edges(topology: dict[str, Any], reachable: set[str]) -> set[tuple[str, str]]:
    return {(origin, target) for origin, targets in (topology.get("adjacency") or {}).items() if origin in reachable for target in targets if target in reachable}


def render_pseudo_chat(source: dict[str, Any]) -> str:
    topology = graph_topology(source)
    reachable = _reachable(topology)
    lines = ["# Pseudo-Chat", "", "<!-- ordo-pseudo-chat: generated -->", ""]
    for vertex_id in sorted(reachable):
        vertex = topology["by_id"][vertex_id]
        label = "Gate" if vertex_id in topology["gates"] else "Node"
        text = str(vertex.get("question") or vertex.get("purpose") or vertex.get("description") or "No analyst-facing text declared.")
        lines.extend([f"## {label}: `{vertex_id}`", f"<!-- ordo-node: {vertex_id} -->", "", text, ""])
        for target in sorted(topology["adjacency"].get(vertex_id) or []):
            if target in reachable:
                lines.extend([f"<!-- ordo-transition: {vertex_id} -> {target} -->", f"- Transition to `{target}`."])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def validate_documentation_graph(source: dict[str, Any], document: str | Path) -> dict[str, Any]:
    path = Path(document)
    if not path.is_file():
        return {"schema_version": "ordo.documentation_graph.v1", "status": "failed", "issues": [{"severity": "error", "code": "DOC_GRAPH_DOCUMENT_MISSING", "message": "pseudo-chat document is missing.", "location": str(path)}]}
    text = path.read_text(encoding="utf-8")
    topology = graph_topology(source)
    reachable = _reachable(topology)
    expected_edges = _edges(topology, reachable)
    documented_nodes = set(NODE_MARKER.findall(text))
    documented_edges = set(EDGE_MARKER.findall(text))
    issues: list[dict[str, Any]] = []
    for node_id in sorted(documented_nodes - set(topology["by_id"])):
        issues.append({"severity": "error", "code": "DOC_GRAPH_NODE_REMOVED", "message": "documentation references a removed graph node or gate.", "location": str(path), "node": node_id})
    for node_id in sorted(documented_nodes & (set(topology["by_id"]) - reachable)):
        issues.append({"severity": "error", "code": "DOC_GRAPH_NODE_UNREACHABLE", "message": "documentation presents an unreachable graph node or gate.", "location": str(path), "node": node_id})
    for node_id in sorted(reachable - documented_nodes):
        issues.append({"severity": "error", "code": "DOC_GRAPH_NODE_UNDOCUMENTED", "message": "reachable graph node or gate has no pseudo-chat entry.", "location": str(path), "node": node_id})
    for edge in sorted(documented_edges - expected_edges):
        issues.append({"severity": "error", "code": "DOC_GRAPH_TRANSITION_STALE", "message": "documentation describes a removed or unreachable transition.", "location": str(path), "transition": list(edge)})
    for edge in sorted(expected_edges - documented_edges):
        issues.append({"severity": "error", "code": "DOC_GRAPH_TRANSITION_UNDOCUMENTED", "message": "reachable graph transition is missing from pseudo-chat.", "location": str(path), "transition": list(edge)})
    return {
        "schema_version": "ordo.documentation_graph.v1",
        "status": "passed" if not issues else "failed",
        "document": str(path),
        "summary": {"reachable_vertices": len(reachable), "reachable_transitions": len(expected_edges), "errors": len(issues)},
        "issues": issues,
    }
