from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
import json

TRACE_FORMAT = "ordo-execution-trace.v1"
REPLAY_CONTRACT_VERSION = "1.0"
DEFAULT_TRACE_PATH = "runtime/execution_trace.json"
CAPTURE_LEVELS = {"minimal", "standard", "full", "audit"}
REPLAY_MODES = {"deterministic", "re_evaluate", "simulation", "audit_only"}
TERMINAL_STATUS_TO_EVENT = {
    "completed": "run_completed",
    "failed": "run_failed",
    "cancelled": "run_cancelled",
    "interrupted": "run_failed",
}
CAPTURE_EVENT_CLASSES = {
    "minimal": {"run", "path", "gate", "output", "error"},
    "standard": {"run", "path", "gate", "output", "error", "input", "decision", "state", "approval"},
    "full": {"run", "path", "gate", "output", "error", "input", "decision", "state", "approval", "action", "template", "checkpoint", "warning"},
    "audit": {"*"},
}
EVENT_CLASS = {
    "run_started": "run", "run_paused": "run", "run_resumed": "run", "run_completed": "run",
    "run_failed": "run", "run_cancelled": "run", "node_entered": "path", "node_exited": "path",
    "path_selected": "path", "phase_changed": "path", "question_asked": "input", "user_input": "input",
    "input_validated": "input", "input_rejected": "input", "field_assigned": "state", "field_cleared": "state",
    "action_started": "action", "action_completed": "action", "action_failed": "error", "external_call": "action",
    "decision_evaluated": "decision", "decision_selected": "decision", "branch_selected": "decision",
    "gate_evaluated": "gate", "gate_passed": "gate", "gate_failed": "gate", "gate_overridden": "gate",
    "state_snapshot": "state", "state_changed": "state", "template_selected": "template",
    "artifact_generation_started": "output", "artifact_generated": "output", "artifact_updated": "output",
    "artifact_validation": "output", "warning_raised": "warning", "error_raised": "error",
    "recovery_applied": "error", "approval_requested": "approval", "approval_granted": "approval",
    "approval_rejected": "approval", "checkpoint_created": "checkpoint",
}
SENSITIVE_KEYS = {"password", "secret", "token", "access_token", "api_key", "authorization", "credential"}
DECISION_TRACE_FORBIDDEN_KEYS = {
    "chain_of_thought", "hidden_chain_of_thought", "private_reasoning",
    "internal_monologue", "scratchpad", "raw_model_reasoning",
}
DECISION_SUMMARY_MAX_LENGTH = 4000


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_checksum(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()


def state_fingerprint(state: dict[str, Any] | None) -> dict[str, Any]:
    """Return a non-secret, machine-comparable state record for replay."""
    value = state if isinstance(state, dict) else {}
    return {
        "checksum": canonical_checksum(value),
        "value": _redact(value),
    }


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, child in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                out[key] = {"value_redacted": True}
            else:
                out[key] = _redact(child)
        return out
    if isinstance(value, list):
        return [_redact(x) for x in value]
    return value


def normalize_policy(value: dict[str, Any] | None) -> dict[str, Any]:
    raw = deepcopy(value or {})
    capture = raw.get("capture_level", "standard")
    if capture not in CAPTURE_LEVELS:
        raise ValueError(f"unsupported EXECUTION_TRACE capture_level: {capture}")
    replay = raw.get("replay") if isinstance(raw.get("replay"), dict) else {}
    replay_mode = replay.get("replay_mode", "deterministic")
    if replay_mode not in REPLAY_MODES:
        raise ValueError(f"unsupported EXECUTION_TRACE replay_mode: {replay_mode}")
    storage = raw.get("storage") if isinstance(raw.get("storage"), dict) else {}
    return {
        "enabled": bool(raw.get("enabled", True)),
        "version": str(raw.get("version", "1.0")),
        "capture_level": capture,
        "storage": {
            "format": storage.get("format", "json"),
            "path": storage.get("path", DEFAULT_TRACE_PATH),
            "append_only": bool(storage.get("append_only", True)),
        },
        "replay": {
            "replayable": bool(replay.get("replayable", True)),
            "replay_mode": replay_mode,
            "required_inputs_preserved": bool(replay.get("required_inputs_preserved", True)),
            "external_dependencies": replay.get("external_dependencies", {"strategy": "recorded"}),
            "sensitive_values": replay.get("sensitive_values", {"strategy": "redacted"}),
        },
    }


def trace_path(root: str | Path, policy: dict[str, Any] | None = None) -> Path:
    normalized = normalize_policy(policy)
    return Path(root) / str(normalized["storage"]["path"])


def event_is_captured(capture_level: str, event_type: str) -> bool:
    if capture_level not in CAPTURE_LEVELS:
        return False
    event_class = EVENT_CLASS.get(event_type, "action")
    allowed = CAPTURE_EVENT_CLASSES[capture_level]
    return "*" in allowed or event_class in allowed


def initialize_execution_trace(
    root: str | Path,
    *,
    policy: dict[str, Any] | None,
    run_id: str,
    process_id: str,
    process_version: str,
    execution_mode: str,
    entry_point: str,
    actor_type: str = "runtime",
    actor_id: str | None = None,
    session_id: str | None = None,
    program_id: str | None = None,
    runtime_mode: str = "full_runtime",
    trace_source: str = "runtime_enforced",
    initial_state: dict[str, Any] | None = None,
    playbook_identity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = normalize_policy(policy)
    if not normalized["enabled"]:
        return {"enabled": False, "status": "disabled", "path": None}
    path = trace_path(root, normalized)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"execution trace already exists: {path}")
    trace = {
        "trace_format": TRACE_FORMAT,
        "id": f"trace.{run_id}",
        "version": normalized["version"],
        "run": {
            "run_id": run_id,
            "process_id": process_id,
            "process_version": process_version,
            "program_id": program_id,
            "execution_mode": execution_mode,
            "runtime_mode": runtime_mode,
            "trace_source": trace_source,
        },
        "status": "running",
        "started_at": utc_now(),
        "finished_at": None,
        "actor": {"actor_type": actor_type, "actor_id": actor_id, "session_id": session_id},
        "source": {"entry_point": entry_point, "input_refs": []},
        "capture_level": normalized["capture_level"],
        "events": [],
        "final_state": None,
        "outputs": [],
        "replay": normalized["replay"],
        "replay_contract": {
            "version": REPLAY_CONTRACT_VERSION,
            "initial_state": state_fingerprint(initial_state),
            "final_state": None,
            "playbook": deepcopy(playbook_identity or {}),
            "records_complete": True,
        },
        "integrity": {"event_count": 0, "sequence_complete": True, "checksum": None, "previous_trace_checksum": None},
    }
    _write_trace(path, trace)
    append_execution_trace_event(root, policy=normalized, event_type="run_started", actor={"actor_type": actor_type, "actor_id": actor_id}, payload={"entry_point": entry_point}, outcome={"status": "accepted"})
    return load_execution_trace(root, normalized)


def _write_trace(path: Path, trace: dict[str, Any]) -> None:
    value = deepcopy(trace)
    value.setdefault("integrity", {})["event_count"] = len(value.get("events", []))
    value["integrity"]["sequence_complete"] = all(
        int(event.get("sequence", -1)) == idx for idx, event in enumerate(value.get("events", []), start=1)
    )
    value["integrity"]["checksum"] = None
    checksum = canonical_checksum(value)
    value["integrity"]["checksum"] = checksum
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_execution_trace(root: str | Path, policy: dict[str, Any] | None = None) -> dict[str, Any]:
    path = trace_path(root, policy)
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def append_execution_trace_event(
    root: str | Path,
    *,
    policy: dict[str, Any] | None,
    event_type: str,
    actor: dict[str, Any],
    payload: dict[str, Any] | None = None,
    outcome: dict[str, Any] | None = None,
    location: dict[str, Any] | None = None,
    state_effect: dict[str, Any] | None = None,
    correlation: dict[str, Any] | None = None,
    occurred_at: str | None = None,
) -> dict[str, Any]:
    normalized = normalize_policy(policy)
    if not normalized["enabled"]:
        return {"captured": False, "reason": "trace_disabled"}
    if event_type not in EVENT_CLASS:
        raise ValueError(f"unsupported EXECUTION_TRACE event_type: {event_type}")
    path = trace_path(root, normalized)
    trace = load_execution_trace(root, normalized)
    if trace.get("status") in TERMINAL_STATUS_TO_EVENT:
        raise RuntimeError("cannot append to terminal EXECUTION_TRACE")
    if not event_is_captured(normalized["capture_level"], event_type):
        return {"captured": False, "reason": "capture_level_filtered", "event_type": event_type}
    seq = len(trace.get("events", [])) + 1
    safe_payload = _redact(payload or {})
    event = {
        "sequence": seq,
        "event_id": f"event-{seq:06d}",
        "event_type": event_type,
        "occurred_at": occurred_at or utc_now(),
        "location": location or {"node_id": None, "path_id": None, "phase_id": None},
        "actor": {"actor_type": actor.get("actor_type", "runtime"), "actor_id": actor.get("actor_id")},
        "payload": safe_payload,
        "state_effect": state_effect or {"changed": False, "before_ref": None, "after_ref": None, "diff_ref": None},
        "correlation": correlation or {"parent_event_id": None, "decision_id": None, "gate_id": None, "output_id": None},
        "outcome": outcome or {"status": "completed", "reason_code": None, "summary": None},
    }
    event["replay_record"] = _build_replay_record(event)
    trace["events"].append(event)
    if event_type == "artifact_generated":
        output_id = event["correlation"].get("output_id") or event["payload"].get("output_id")
        if output_id:
            trace.setdefault("outputs", []).append({
                "output_id": output_id,
                "artifact_ref": event["payload"].get("artifact_ref"),
                "checksum": event["payload"].get("checksum"),
            })
    _write_trace(path, trace)
    return {"captured": True, "event": event, "path": str(path)}


def _build_replay_record(event: dict[str, Any]) -> dict[str, Any]:
    """Normalize all runtime events into one auditable replay shape.

    The record intentionally stores an explainable decision summary, never private
    model reasoning.  Missing data is explicit instead of being inferred during a
    later replay.
    """
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    location = event.get("location") if isinstance(event.get("location"), dict) else {}
    state_effect = event.get("state_effect") if isinstance(event.get("state_effect"), dict) else {}
    correlation = event.get("correlation") if isinstance(event.get("correlation"), dict) else {}
    outcome = event.get("outcome") if isinstance(event.get("outcome"), dict) else {}
    decision = payload.get("decision_record") if isinstance(payload.get("decision_record"), dict) else {}
    event_type = str(event.get("event_type") or "")
    evidence_class = "runtime_only"
    if event_type == "decision_selected":
        evidence_class = "accepted_decision"
    elif event_type in {"gate_failed", "error_raised", "run_failed"}:
        evidence_class = "blocker"
    elif event_type in {"warning_raised", "input_rejected"}:
        evidence_class = "discrepancy"
    return {
        "node_id": decision.get("node_id", location.get("node_id")),
        "phase_id": location.get("phase_id"),
        "analyst_input": decision.get("analyst_response", payload.get("answer", payload.get("input"))),
        "expected_route": decision.get("selected_transition", payload.get("next_node", payload.get("transition"))),
        "state_before_ref": decision.get("state_before_ref", state_effect.get("before_ref")),
        "state_after_ref": decision.get("state_after_ref", state_effect.get("after_ref")),
        "checkpoint_id": payload.get("checkpoint_id", payload.get("checkpoint", {}).get("id") if isinstance(payload.get("checkpoint"), dict) else None),
        "decision_id": decision.get("replay_anchor", correlation.get("decision_id")),
        "evidence_class": evidence_class,
        "reason_code": decision.get("reason_code", outcome.get("reason_code")),
    }


def append_decision_interaction_event(
    root: str | Path,
    *,
    policy: dict[str, Any] | None,
    actor: dict[str, Any],
    node_id: str,
    question_text: str,
    analyst_response: Any,
    selected_transition: str | None,
    decision_summary: str,
    question_ref: str | None = None,
    question_context_digest: str | None = None,
    applicable_rules: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    state_before_ref: str | None = None,
    state_after_ref: str | None = None,
    state_diff: dict[str, Any] | None = None,
    replay_anchor: str | None = None,
    reason_code: str | None = None,
    occurred_at: str | None = None,
) -> dict[str, Any]:
    """Record an auditable node interaction without persisting hidden reasoning."""
    if not node_id or not question_text:
        raise ValueError("decision interaction requires node_id and question_text")
    if not isinstance(decision_summary, str) or not decision_summary.strip():
        raise ValueError("decision interaction requires a non-empty decision_summary")
    if len(decision_summary) > DECISION_SUMMARY_MAX_LENGTH:
        raise ValueError("decision_summary exceeds the safe maximum length")
    record = {
        "node_id": node_id,
        "question_text": question_text,
        "question_ref": question_ref,
        "question_context_digest": question_context_digest,
        "analyst_response": analyst_response,
        "selected_transition": selected_transition,
        "applicable_rules": list(applicable_rules or []),
        "evidence_refs": list(evidence_refs or []),
        "state_before_ref": state_before_ref,
        "state_after_ref": state_after_ref,
        "state_diff": state_diff or {},
        "replay_anchor": replay_anchor,
        "reason_code": reason_code,
        "decision_summary": decision_summary.strip(),
        "summary_kind": "bounded_redacted_model_report",
        "hidden_chain_of_thought_persisted": False,
    }
    forbidden = DECISION_TRACE_FORBIDDEN_KEYS.intersection(record)
    if forbidden:
        raise ValueError(f"decision interaction contains forbidden reasoning fields: {sorted(forbidden)}")
    return append_execution_trace_event(
        root,
        policy=policy,
        event_type="decision_selected",
        actor=actor,
        location={"node_id": node_id, "path_id": None, "phase_id": None},
        payload={"decision_record": record},
        state_effect={
            "changed": bool(state_diff),
            "before_ref": state_before_ref,
            "after_ref": state_after_ref,
            "diff_ref": None,
        },
        correlation={"parent_event_id": None, "decision_id": replay_anchor, "gate_id": None, "output_id": None},
        outcome={"status": "selected", "reason_code": reason_code, "summary": decision_summary.strip()},
        occurred_at=occurred_at,
    )


def finalize_execution_trace(
    root: str | Path,
    *,
    policy: dict[str, Any] | None,
    status: str,
    final_state: dict[str, Any] | None = None,
    actor: dict[str, Any] | None = None,
    reason_code: str | None = None,
) -> dict[str, Any]:
    if status not in TERMINAL_STATUS_TO_EVENT:
        raise ValueError(f"unsupported terminal EXECUTION_TRACE status: {status}")
    normalized = normalize_policy(policy)
    if not normalized["enabled"]:
        return {"enabled": False, "status": "disabled"}
    event_type = TERMINAL_STATUS_TO_EVENT[status]
    append_execution_trace_event(
        root,
        policy=normalized,
        event_type=event_type,
        actor=actor or {"actor_type": "runtime"},
        payload={},
        outcome={"status": "completed" if status == "completed" else "failed", "reason_code": reason_code, "summary": None},
    )
    path = trace_path(root, normalized)
    trace = load_execution_trace(root, normalized)
    trace["status"] = status
    trace["finished_at"] = utc_now()
    trace["final_state"] = final_state
    trace.setdefault("replay_contract", {})["final_state"] = state_fingerprint(final_state)
    _write_trace(path, trace)
    trace = load_execution_trace(root, normalized)
    report = validate_execution_trace(trace)
    if not report["valid"]:
        raise RuntimeError(json.dumps(report["issues"], ensure_ascii=False))
    return trace


def validate_execution_trace(trace: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    events = trace.get("events") if isinstance(trace.get("events"), list) else []
    for idx, event in enumerate(events, start=1):
        if event.get("sequence") != idx:
            issues.append({"code": "ORDO-EXEC-TRACE-001", "message": f"sequence gap at {idx}"})
        if event.get("event_type") not in EVENT_CLASS:
            issues.append({"code": "ORDO-EXEC-TRACE-002", "message": f"unknown event type at {idx}"})
        record = event.get("replay_record")
        if not isinstance(record, dict):
            issues.append({"code": "ORDO-EXEC-TRACE-011", "message": f"event {idx} has no replay_record"})
        elif record.get("evidence_class") not in {"accepted_decision", "blocker", "discrepancy", "runtime_only"}:
            issues.append({"code": "ORDO-EXEC-TRACE-012", "message": f"event {idx} has invalid replay evidence_class"})
    integrity = trace.get("integrity") if isinstance(trace.get("integrity"), dict) else {}
    if integrity.get("event_count") != len(events):
        issues.append({"code": "ORDO-EXEC-TRACE-003", "message": "event_count mismatch"})
    if not integrity.get("sequence_complete", False):
        issues.append({"code": "ORDO-EXEC-TRACE-004", "message": "sequence_complete is false"})
    expected = deepcopy(trace)
    expected.setdefault("integrity", {})["checksum"] = None
    if integrity.get("checksum") != canonical_checksum(expected):
        issues.append({"code": "ORDO-EXEC-TRACE-005", "message": "checksum mismatch"})
    status = trace.get("status")
    if status in TERMINAL_STATUS_TO_EVENT:
        if not trace.get("finished_at"):
            issues.append({"code": "ORDO-EXEC-TRACE-006", "message": "terminal trace missing finished_at"})
        expected_event = TERMINAL_STATUS_TO_EVENT[status]
        if not events or events[-1].get("event_type") != expected_event:
            issues.append({"code": "ORDO-EXEC-TRACE-007", "message": "terminal trace missing terminal event"})
    replay = trace.get("replay") if isinstance(trace.get("replay"), dict) else {}
    if replay.get("replayable") and not replay.get("required_inputs_preserved"):
        issues.append({"code": "ORDO-EXEC-TRACE-008", "message": "replayable trace does not preserve required inputs"})
    contract = trace.get("replay_contract")
    if not isinstance(contract, dict):
        issues.append({"code": "ORDO-EXEC-TRACE-013", "message": "trace has no replay_contract"})
    elif not isinstance(contract.get("initial_state"), dict):
        issues.append({"code": "ORDO-EXEC-TRACE-014", "message": "replay contract has no initial state fingerprint"})
    return {"valid": not issues, "issues": issues, "event_count": len(events), "status": status}


def replay_plan(trace: dict[str, Any], *, mode: str | None = None) -> dict[str, Any]:
    report = validate_execution_trace(trace)
    if not report["valid"]:
        return {"ready": False, "issues": report["issues"], "steps": []}
    replay = trace.get("replay") or {}
    selected_mode = mode or replay.get("replay_mode", "deterministic")
    if selected_mode not in REPLAY_MODES:
        return {"ready": False, "issues": [{"code": "ORDO-EXEC-TRACE-009", "message": "unsupported replay mode"}], "steps": []}
    if selected_mode != "audit_only" and not replay.get("replayable"):
        return {"ready": False, "issues": [{"code": "ORDO-EXEC-TRACE-010", "message": "trace is not replayable"}], "steps": []}
    steps = []
    replay_types = {"user_input", "decision_selected", "branch_selected", "gate_passed", "gate_failed", "artifact_generated"}
    for event in trace.get("events", []):
        if selected_mode == "audit_only" or event.get("event_type") in replay_types:
            steps.append({
                "sequence": event.get("sequence"),
                "event_type": event.get("event_type"),
                "location": event.get("location"),
                "payload": event.get("payload"),
                "outcome": event.get("outcome"),
                "side_effects_allowed": selected_mode not in {"simulation", "audit_only"},
                "re_evaluate": selected_mode == "re_evaluate",
            })
    return {"ready": True, "mode": selected_mode, "run_id": (trace.get("run") or {}).get("run_id"), "steps": steps, "issues": []}
