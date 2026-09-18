from __future__ import annotations

import re
from typing import Any

from .graph_contract import dynamic_route_declarations, failure_route_declarations, vertex_route_declarations


# These values are gate control effects, rather than references to another
# graph vertex. A value such as "G_MISSING" remains a real target and is
# therefore still rejected when it is not declared.
GATE_CONTROL_OUTCOMES = {"block", "continue", "retry", "stop", "warn"}


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

    contract = source.get("graph_contract") or {}
    entry = contract.get("entry_node") or (nodes[0].get("id") if nodes else None)
    external_terminals = set(contract.get("external_terminal_targets", []) or [])
    known_targets = set(node_by_id) | set(gate_by_id) | external_terminals
    node_declarations = {
        vertex_id: [
            *vertex_route_declarations(vertex, vertex_id=vertex_id, vertex_kind="node"),
            *failure_route_declarations(vertex, vertex_id=vertex_id, vertex_kind="node"),
        ]
        for vertex_id, vertex in node_by_id.items()
    }
    gate_declarations = {
        vertex_id: [
            *vertex_route_declarations(vertex, vertex_id=vertex_id, vertex_kind="gate"),
            *failure_route_declarations(vertex, vertex_id=vertex_id, vertex_kind="gate"),
        ]
        for vertex_id, vertex in gate_by_id.items()
    }
    node_edges = {vertex_id: [item.target for item in items] for vertex_id, items in node_declarations.items()}
    # Catalogue-only gates remain non-vertices unless referenced by a process
    # route. Control effects are not graph destinations.
    gate_edges = {
        vertex_id: [item.target for item in items if item.target.casefold() not in GATE_CONTROL_OUTCOMES and (item.target in known_targets or re.match(r"^(?:N|G|STOP|END|OUT)_", item.target) is not None)]
        for vertex_id, items in gate_declarations.items()
    }
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
    dynamic_declarations = dynamic_route_declarations(contract)
    for declaration in dynamic_declarations:
        if declaration.source in adjacency:
            adjacency[declaration.source].append(declaration.target)
    return {
        "nodes": node_by_id,
        "gates": gate_by_id,
        "duplicate_ids": duplicate_ids,
        "by_id": by_id,
        "adjacency": adjacency,
        "node_route_declarations": node_declarations,
        "gate_route_declarations": gate_declarations,
        "dynamic_route_declarations": dynamic_declarations,
        "executable_gate_ids": executable_gate_ids,
        "entry": entry,
    }
