from __future__ import annotations

from typing import Any
import copy

CONTROL_CLASSES = {"pause_request", "resume_request", "exit_request"}
SAFETY_CLASSES = {"unsafe_or_emergency_message"}
MUTATING_CLASSES = {
    "answer_to_active_question",
    "correction",
    "backtrack_request",
    "requirement_change",
}
NON_MUTATING_CLASSES = {
    "clarification",
    "process_meta_question",
    "related_context",
    "unrelated_topic",
    "unclassifiable_input",
}
ALL_CLASSES = CONTROL_CLASSES | SAFETY_CLASSES | MUTATING_CLASSES | NON_MUTATING_CLASSES


def _runtime_meta(state: dict[str, Any]) -> dict[str, Any]:
    return state.setdefault("_csg_runtime", {
        "status": "active",
        "suspended_node": None,
        "exit_reason": None,
        "last_classification": None,
        "last_action": None,
    })


def _event(event_type: str, **payload: Any) -> dict[str, Any]:
    return {"type": event_type, **payload}


def _apply_update(target: dict[str, Any], update: dict[str, Any]) -> None:
    for key, value in update.items():
        parts = str(key).split(".")
        cur = target
        for part in parts[:-1]:
            cur = cur.setdefault(part, {})
        cur[parts[-1]] = value


def enforce_csg_proposal(
    csg: dict[str, Any] | None,
    state: dict[str, Any],
    proposal: dict[str, Any],
) -> dict[str, Any]:
    """Validate and apply one model proposal under CSG runtime rules.

    The function never mutates protected process state when a proposal is blocked.
    Runtime control metadata lives under ``_csg_runtime`` and is not considered
    protected business/process state.
    """
    csg = csg or {}
    enabled = bool(csg.get("supported")) and bool(csg.get("enabled"))
    before = copy.deepcopy(state)
    working = copy.deepcopy(state)
    meta = _runtime_meta(working)
    classification = proposal.get("classification")
    action = proposal.get("action")
    update = proposal.get("state_update") or {}
    target_node = proposal.get("target_node")
    events: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []

    if not enabled:
        if update:
            _apply_update(working, update)
        if target_node is not None:
            working["current_node"] = target_node
        state.clear(); state.update(working)
        return {"status": "applied_without_csg", "allowed": True, "events": events, "issues": issues}

    events.append(_event("conversation.deviation.detected", classification=classification, action=action))
    if classification not in ALL_CLASSES:
        issues.append({"code": "CSG_CLASSIFICATION_UNKNOWN", "message": f"Unknown CSG classification: {classification!r}"})
        events.append(_event("conversation.deviation.classified", classification="unclassifiable_input"))
        events.append(_event("runner.action.blocked", reason="unknown_classification"))
        return {"status": "blocked", "allowed": False, "events": events, "issues": issues}

    events.append(_event("conversation.deviation.classified", classification=classification))
    meta["last_classification"] = classification
    meta["last_action"] = action

    if meta.get("status") == "exited" and classification != "resume_request":
        issues.append({"code": "CSG_PROCESS_EXITED", "message": "Process already exited; proposal blocked."})
        events.append(_event("runner.action.blocked", reason="process_exited"))
        return {"status": "blocked", "allowed": False, "events": events, "issues": issues}

    if classification == "pause_request":
        events.append(_event("process.pause.requested"))
        if meta.get("status") == "paused":
            issues.append({"code": "CSG_ALREADY_PAUSED", "message": "Process is already paused."})
            events.append(_event("runner.action.blocked", reason="already_paused"))
            return {"status": "blocked", "allowed": False, "events": events, "issues": issues}
        meta["suspended_node"] = working.get("current_node")
        meta["status"] = "paused"
        events.append(_event("process.paused", suspended_node=meta.get("suspended_node")))

    elif classification == "resume_request":
        events.append(_event("process.resume.requested"))
        if meta.get("status") != "paused":
            issues.append({"code": "CSG_RESUME_WITHOUT_PAUSE", "message": "Resume requires a paused process."})
            events.append(_event("runner.action.blocked", reason="not_paused"))
            return {"status": "blocked", "allowed": False, "events": events, "issues": issues}
        working["current_node"] = meta.get("suspended_node")
        meta["status"] = "active"
        events.append(_event("process.resumed", current_node=working.get("current_node")))

    elif classification == "exit_request":
        events.append(_event("process.exit.requested"))
        meta["status"] = "exited"
        meta["exit_reason"] = proposal.get("reason") or "user_requested_exit"
        working["blocked"] = True
        working["go_no_go"] = "incomplete"
        events.append(_event("process.exited", reason=meta["exit_reason"]))

    elif classification in SAFETY_CLASSES:
        if update or target_node is not None:
            issues.append({"code": "CSG_SAFETY_STATE_MUTATION_BLOCKED", "message": "Safety bypass must not mutate protected process state."})
            events.append(_event("runner.action.blocked", reason="safety_state_mutation"))
            return {"status": "blocked", "allowed": False, "events": events, "issues": issues}
        events.append(_event("conversation.scope_guard.bypassed_for_safety"))

    elif classification in NON_MUTATING_CLASSES:
        if update or target_node is not None:
            issues.append({"code": "CSG_PROTECTED_STATE_MUTATION_BLOCKED", "message": f"{classification} must not mutate protected process state or change node/path."})
            events.append(_event("runner.action.blocked", reason="protected_state_mutation"))
            return {"status": "blocked", "allowed": False, "events": events, "issues": issues}
        if classification == "unrelated_topic":
            events.append(_event("conversation.redirect.emitted"))

    elif classification in MUTATING_CLASSES:
        if meta.get("status") == "paused":
            issues.append({"code": "CSG_PROCESS_PAUSED", "message": "Mutating proposal blocked while process is paused."})
            events.append(_event("runner.action.blocked", reason="process_paused"))
            return {"status": "blocked", "allowed": False, "events": events, "issues": issues}
        if update:
            _apply_update(working, update)
        if target_node is not None:
            working["current_node"] = target_node

    state.clear(); state.update(working)
    protected_before = {k: v for k, v in before.items() if k != "_csg_runtime"}
    protected_after = {k: v for k, v in state.items() if k != "_csg_runtime"}
    events.append(_event(
        "runner.csg.decision",
        decision="applied",
        classification=classification,
        protected_state_changed=protected_before != protected_after,
    ))
    return {"status": "applied", "allowed": True, "events": events, "issues": issues}


def apply_csg_events(source: dict[str, Any], state: dict[str, Any], proposals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    csg = source.get("conversation_scope_guard") or {}
    results = []
    for index, proposal in enumerate(proposals or []):
        result = enforce_csg_proposal(csg, state, proposal)
        result["index"] = index
        result["proposal"] = proposal
        results.append(result)
    return results
