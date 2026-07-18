from __future__ import annotations

from typing import Any

CHECKPOINT_STATUSES = {"open", "incomplete", "closed", "blocked", "not_applicable"}
CHECKPOINT_ERROR_CODES = {
    "ORDO-CHECKPOINT-001": "node advanced before current contract closed",
    "ORDO-CHECKPOINT-002": "earlier mandatory node incomplete",
    "ORDO-CHECKPOINT-003": "multiple node contracts merged without allow_batch_confirmation",
    "ORDO-CHECKPOINT-004": "missing checkpoint table in run_state",
    "ORDO-CHECKPOINT-005": "next-step ignored earliest_incomplete_node",
    "ORDO-CHECKPOINT-006": "generated output requested while checkpoint gaps remain",
}


def _present(value: Any) -> bool:
    return value not in (None, False, "", [], {})


def _node_update_fields(node: dict[str, Any]) -> list[str]:
    """Return state fields that this runtime node is responsible for closing.

    Ordo nodes can use either a simple `on_answer.update_state` mapping or an
    enum/list of branches under `on_answer`. For checkpointing, the field union
    is enough to decide whether a node has open required fields.
    """
    explicit = node.get("required_fields")
    if isinstance(explicit, list):
        return [str(x) for x in explicit]
    result: list[str] = []
    on_answer = node.get("on_answer")
    if isinstance(on_answer, dict):
        direct = on_answer.get("update_state")
        if isinstance(direct, dict):
            result.extend(str(k) for k in direct.keys())
        for branch in on_answer.values():
            if isinstance(branch, dict):
                updates = branch.get("update_state")
                if isinstance(updates, dict):
                    result.extend(str(k) for k in updates.keys())
    # Preserve order and remove duplicates.
    seen: set[str] = set()
    deduped: list[str] = []
    for field in result:
        if field not in seen:
            deduped.append(field)
            seen.add(field)
    return deduped


def _answered_node_ids_from_state(state: dict[str, Any]) -> list[str]:
    answered = state.get("answered_questions") or []
    ids: list[str] = []
    if isinstance(answered, list):
        for item in answered:
            if isinstance(item, str):
                ids.append(item)
            elif isinstance(item, dict):
                node_id = item.get("node") or item.get("node_id") or item.get("id")
                if node_id:
                    ids.append(str(node_id))
    return ids


def build_checkpoint_report(source: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    nodes = source.get("nodes", []) or []
    allow_batch = bool(source.get("allow_batch_confirmation") or ((source.get("runtime") or {}).get("allow_batch_confirmation")))
    checkpoint_table: dict[str, Any] = {}
    earliest_incomplete_node: str | None = None
    open_required_fields: list[str] = []
    last_closed_node: str | None = None

    node_ids = [str(n.get("id")) for n in nodes if n.get("id")]
    explicit_current = state.get("current_node") if isinstance(state, dict) else None
    answered_node_ids = _answered_node_ids_from_state(state)
    current_node = explicit_current or (answered_node_ids[-1] if answered_node_ids else (node_ids[0] if node_ids else ""))

    for node in nodes:
        node_id = str(node.get("id"))
        required_fields = _node_update_fields(node)
        confirmed_fields = [field for field in required_fields if _present(state.get(field))]
        gaps = [field for field in required_fields if field not in confirmed_fields]
        if not required_fields:
            status = "not_applicable"
        elif not gaps:
            status = "closed"
            last_closed_node = node_id
        elif confirmed_fields:
            status = "incomplete"
        else:
            status = "open"
        if required_fields and gaps and earliest_incomplete_node is None:
            earliest_incomplete_node = node_id
            open_required_fields = gaps
        checkpoint_table[node_id] = {
            "status": status,
            "required_fields": required_fields,
            "confirmed_fields": confirmed_fields,
            "open_gaps": gaps,
            "next_allowed": "" if gaps else _next_node_id(node_ids, node_id),
        }

    forward_allowed = earliest_incomplete_node is None
    node_merge_attempt_detected = bool(state.get("node_merge_attempt_detected"))
    conversation_step_node_ids = state.get("conversation_step_node_ids") or state.get("attempted_node_ids") or []
    if isinstance(conversation_step_node_ids, list) and len(set(map(str, conversation_step_node_ids))) > 1 and not allow_batch:
        node_merge_attempt_detected = True
    issues: list[dict[str, Any]] = []
    if state and "checkpoint_table" not in state and state.get("requires_checkpoint_table") is True:
        issues.append(_issue("ORDO-CHECKPOINT-004", "missing checkpoint table in run_state", location="run_state.checkpoint_table"))
    if earliest_incomplete_node:
        issues.append(_issue("ORDO-CHECKPOINT-002", "earlier mandatory node incomplete", location=earliest_incomplete_node))
    if node_merge_attempt_detected:
        issues.append(_issue("ORDO-CHECKPOINT-003", "multiple node contracts merged without allow_batch_confirmation", location="run_state.conversation_step_node_ids"))

    return {
        "mode": "runtime_checkpoint_discipline",
        "status": "passed" if not issues else "blocked",
        "node_closure_status_values": sorted(CHECKPOINT_STATUSES),
        "current_node": current_node,
        "last_closed_node": last_closed_node or "",
        "earliest_incomplete_node": earliest_incomplete_node or "",
        "checkpoint_table": checkpoint_table,
        "forward_allowed": forward_allowed and not node_merge_attempt_detected,
        "open_required_fields": open_required_fields,
        "node_merge_attempt_detected": node_merge_attempt_detected,
        "allow_batch_confirmation": allow_batch,
        "next_allowed_node": earliest_incomplete_node or _next_node_id(node_ids, str(current_node)) or "",
        "issues": issues,
    }


def enrich_state_with_checkpoint(state: dict[str, Any], checkpoint: dict[str, Any]) -> dict[str, Any]:
    state = dict(state)
    state["last_closed_node"] = checkpoint.get("last_closed_node", "")
    state["earliest_incomplete_node"] = checkpoint.get("earliest_incomplete_node", "")
    state["checkpoint_table"] = checkpoint.get("checkpoint_table", {})
    state["forward_allowed"] = checkpoint.get("forward_allowed", False)
    state["open_required_fields"] = checkpoint.get("open_required_fields", [])
    state["node_merge_attempt_detected"] = checkpoint.get("node_merge_attempt_detected", False)
    return state


def _next_node_id(node_ids: list[str], node_id: str) -> str:
    try:
        idx = node_ids.index(node_id)
    except ValueError:
        return ""
    if idx + 1 < len(node_ids):
        return node_ids[idx + 1]
    return ""


def _issue(code: str, message: str, *, location: str | None = None, severity: str = "error") -> dict[str, Any]:
    return {"severity": severity, "code": code, "message": message, "location": location}
