from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class TransitionProvenanceIssue:
    severity: str
    code: str
    message: str
    location: str
    source_node: str | None = None
    target_node: str | None = None
    direction: str | None = None


def transition_targets(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "next" and isinstance(child, str):
                out.append(child)
            else:
                out.extend(transition_targets(child))
    elif isinstance(value, list):
        for child in value:
            out.extend(transition_targets(child))
    return out


def provenance_contract(source: dict[str, Any]) -> dict[str, Any]:
    graph = source.get("graph_contract") or {}
    contract = graph.get("transition_provenance") or {}
    return contract if isinstance(contract, dict) else {}


def validate_transition_provenance(source: dict[str, Any]) -> dict[str, Any]:
    contract = provenance_contract(source)
    if not contract.get("enabled", False):
        return {"status": "not_enabled", "summary": {"errors": 0, "warnings": 0, "checked_edges": 0}, "issues": []}

    issues: list[TransitionProvenanceIssue] = []
    nodes = [n for n in source.get("nodes", []) or [] if isinstance(n, dict) and n.get("id")]
    by_id = {str(n["id"]): n for n in nodes}
    ids = set(by_id)
    external = set((source.get("graph_contract") or {}).get("external_terminal_targets", []) or [])
    entry = (source.get("graph_contract") or {}).get("entry_node")
    strict = contract.get("mode", "strict") == "strict"

    outbound: dict[str, set[str]] = {
        node_id: {t for t in transition_targets(node) if t in ids}
        for node_id, node in by_id.items()
    }
    inbound: dict[str, set[str]] = {
        node_id: set(node.get("allowed_from") or node.get("incoming_from") or [])
        for node_id, node in by_id.items()
    }

    for node_id, declared in inbound.items():
        for pred in sorted(declared):
            if pred not in ids:
                issues.append(TransitionProvenanceIssue("error", "GRAPH_INBOUND_SOURCE_MISSING", f"Inbound predecessor {pred!r} does not exist.", f"nodes[{node_id}].allowed_from", pred, node_id, "inbound"))
            elif node_id not in outbound.get(pred, set()):
                issues.append(TransitionProvenanceIssue("error", "GRAPH_INBOUND_WITHOUT_OUTBOUND", f"Node {node_id} accepts {pred}, but {pred} has no direct outbound edge to {node_id}.", f"nodes[{node_id}].allowed_from", pred, node_id, "inbound"))

    checked = 0
    for source_id, targets in outbound.items():
        for target_id in sorted(targets):
            checked += 1
            if source_id not in inbound.get(target_id, set()):
                issues.append(TransitionProvenanceIssue("error" if strict else "warning", "GRAPH_OUTBOUND_NOT_ACCEPTED", f"Direct edge {source_id} -> {target_id} is not accepted by target allowed_from.", f"nodes[{target_id}].allowed_from", source_id, target_id, "outbound"))

    for node_id, node in by_id.items():
        if node_id == entry:
            modes = set(node.get("entry_modes") or [])
            if "root" not in modes:
                issues.append(TransitionProvenanceIssue("error", "GRAPH_ROOT_ENTRY_MODE_MISSING", "Entry node must declare entry_modes: [root] (additional explicit modes are allowed).", f"nodes[{node_id}].entry_modes", None, node_id, "entry"))
        elif strict and not inbound.get(node_id) and not set(node.get("entry_modes") or []):
            issues.append(TransitionProvenanceIssue("error", "GRAPH_INBOUND_DECLARATION_MISSING", f"Non-entry node {node_id} must declare a direct predecessor or an explicit entry mode.", f"nodes[{node_id}].allowed_from", None, node_id, "inbound"))

    errors=[asdict(i) for i in issues if i.severity=="error"]
    warnings=[asdict(i) for i in issues if i.severity=="warning"]
    return {"status": "passed" if not errors else "failed", "summary": {"errors": len(errors), "warnings": len(warnings), "checked_edges": checked}, "issues": [asdict(i) for i in issues]}


def validate_node_entry(source: dict[str, Any], *, target_node_id: str, previous_node_id: str | None, entry_mode: str = "transition") -> dict[str, Any]:
    contract = provenance_contract(source)
    if not contract.get("enabled", False):
        return {"status": "passed", "mode": "transition_provenance_not_enabled", "issues": []}
    nodes={str(n.get("id")): n for n in source.get("nodes", []) or [] if isinstance(n, dict) and n.get("id")}
    target=nodes.get(target_node_id)
    if target is None:
        return {"status":"blocked", "mode":"transition_provenance", "issues":[{"severity":"error","code":"RUNTIME_TARGET_NODE_MISSING","message":f"Target node not found: {target_node_id}","source_node":previous_node_id,"target_node":target_node_id,"direction":"entry"}]}
    entry=(source.get("graph_contract") or {}).get("entry_node")
    if previous_node_id in (None, ""):
        allowed_modes=set(target.get("entry_modes") or [])
        if entry_mode in allowed_modes:
            return {"status":"passed","mode":"transition_provenance","entry_mode":entry_mode,"issues":[]}
        return {"status":"blocked","mode":"transition_provenance_recovery","issues":[{"severity":"error","code":"RUNTIME_ENTRY_PROVENANCE_MISSING","message":"Node entry requires previous_node_id or an explicitly allowed entry mode.","source_node":previous_node_id,"target_node":target_node_id,"direction":"entry","entry_mode":entry_mode}]}
    allowed=set(target.get("allowed_from") or target.get("incoming_from") or [])
    if previous_node_id not in allowed:
        return {"status":"blocked","mode":"transition_provenance_recovery","issues":[{"severity":"error","code":"RUNTIME_PREDECESSOR_NOT_ALLOWED","message":f"Node {target_node_id} does not accept direct entry from {previous_node_id}.","source_node":previous_node_id,"target_node":target_node_id,"direction":"inbound","allowed_from":sorted(allowed)}]}
    return {"status":"passed","mode":"transition_provenance","source_node":previous_node_id,"target_node":target_node_id,"issues":[]}


def build_node_context_envelope(source: dict[str, Any], state: dict[str, Any], node_id: str) -> dict[str, Any]:
    nodes={str(n.get("id")): n for n in source.get("nodes", []) or [] if isinstance(n, dict) and n.get("id")}
    node=nodes.get(node_id) or {}
    contract=node.get("node_context") or {}
    required_state=list(contract.get("required_state") or [])
    projected={key: state.get(key) for key in required_state}
    return {
        "node_id": node_id,
        "contract_version": contract.get("version", "1.0"),
        "required_state": required_state,
        "state_projection": projected,
        "knowledge_refs": list(contract.get("knowledge_refs") or []),
        "allowed_tools": list(contract.get("allowed_tools") or []),
        "output_contract": contract.get("output_contract") or {},
        "missing_required_state": [key for key in required_state if key not in state],
    }
