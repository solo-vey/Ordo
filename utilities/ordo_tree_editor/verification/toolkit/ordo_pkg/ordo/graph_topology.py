from __future__ import annotations

import re
from typing import Any


# These values are gate control effects, rather than references to another
# graph vertex. A value such as "G_MISSING" remains a real target and is
# therefore still rejected when it is not declared.
GATE_CONTROL_OUTCOMES = {"block", "continue", "retry", "stop", "warn"}


def transition_targets(value: Any, *, keys: set[str]) -> list[str]:
    """Collect nested string transition targets for the supplied keys."""
    targets: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in keys and isinstance(child, str):
                targets.append(child)
            else:
                targets.extend(transition_targets(child, keys=keys))
    elif isinstance(value, list):
        for child in value:
            targets.extend(transition_targets(child, keys=keys))
    return targets


def gate_targets(gate: dict[str, Any], *, known_targets: set[str]) -> list[str]:
    """Return top-level routing targets declared by an executable gate."""
    targets: list[str] = []
    for key in ("on_pass", "on_fail"):
        target = gate.get(key)
        if (
            isinstance(target, str)
            and target.casefold() not in GATE_CONTROL_OUTCOMES
            and (target in known_targets or re.match(r"^(?:N|G|STOP|END|OUT)_", target) is not None)
        ):
            targets.append(target)
    return targets


def graph_topology(source: dict[str, Any]) -> dict[str, Any]:
    """Project the executable node-and-gate graph from an Ordo source tree.

    The language also permits declarative gate catalogues whose only outcome is
    a control effect such as ``block``. They remain gates for reporting and
    compilation, but are not process vertices until a route reaches them or
    they declare a vertex-to-vertex route themselves.
    """
    nodes = [item for item in source.get("nodes", []) or [] if isinstance(item, dict) and item.get("id")]
    gates = [item for item in source.get("gates", []) or [] if isinstance(item, dict) and item.get("id")]
    node_by_id = {str(item["id"]): item for item in nodes}
    gate_by_id = {str(item["id"]): item for item in gates}
    duplicate_ids = set(node_by_id) & set(gate_by_id)

    node_edges = {vertex_id: transition_targets(vertex, keys={"next"}) for vertex_id, vertex in node_by_id.items()}
    contract = source.get("graph_contract") or {}
    entry = contract.get("entry_node") or (nodes[0].get("id") if nodes else None)
    external_terminals = set(contract.get("external_terminal_targets", []) or [])
    known_targets = set(node_by_id) | set(gate_by_id) | external_terminals
    gate_edges = {vertex_id: gate_targets(vertex, known_targets=known_targets) for vertex_id, vertex in gate_by_id.items()}
    declared_gate_targets = {
        target
        for targets in [*node_edges.values(), *gate_edges.values()]
        for target in targets
        if target in gate_by_id and target not in external_terminals
    }
    executable_gate_ids = {
        *declared_gate_targets,
        *(vertex_id for vertex_id, targets in gate_edges.items() if targets),
    }
    if entry in gate_by_id:
        executable_gate_ids.add(entry)

    by_id = {**node_by_id, **{vertex_id: gate_by_id[vertex_id] for vertex_id in executable_gate_ids}}
    adjacency = {vertex_id: node_edges[vertex_id] for vertex_id in node_by_id}
    adjacency.update({vertex_id: gate_edges[vertex_id] for vertex_id in executable_gate_ids})
    return {
        "nodes": node_by_id,
        "gates": gate_by_id,
        "duplicate_ids": duplicate_ids,
        "by_id": by_id,
        "adjacency": adjacency,
        "executable_gate_ids": executable_gate_ids,
        "entry": entry,
    }
