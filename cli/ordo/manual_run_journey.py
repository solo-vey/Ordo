from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import copy
import hashlib
import json
import os
import tempfile
import yaml

JOURNEY_SCHEMA = "ordo.manual_run.journey.v1"
EVENTS_PATH = "runtime/manual_run_journey.events.jsonl"
JOURNEY_PATH = "runtime/MANUAL_RUN_JOURNEY.yaml"
VALIDATION_REPORT_PATH = "runtime/manual_run_journey_validation_report.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _load_events(root: Path) -> list[dict[str, Any]]:
    path = root / EVENTS_PATH
    if not path.exists():
        return []
    events = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"journey event line {line_no} is not an object")
        events.append(value)
    return events


def _package_identity(root: Path) -> dict[str, Any]:
    playbook_id = root.name
    version = "unknown"
    release = root / "playbook_release.json"
    if release.exists():
        data = json.loads(release.read_text(encoding="utf-8"))
        playbook_id = str(data.get("playbook_id") or playbook_id)
        version = str(data.get("playbook_version") or data.get("version") or version)
    runtime = root / "ordo.runtime.json"
    if runtime.exists():
        data = json.loads(runtime.read_text(encoding="utf-8"))
        playbook_id = str(data.get("package_id") or playbook_id)
        version = str(data.get("package_version") or version)
    package_digest = ""
    sums = root / "SHA256SUMS.txt"
    if sums.exists():
        package_digest = "sha256:" + hashlib.sha256(sums.read_bytes()).hexdigest()
    return {"id": playbook_id, "version": version, "package_sha256": package_digest}


def _summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "questions_asked": sum(1 for e in events if e.get("event_type") == "question_answer"),
        "accepted_answers": sum(1 for e in events if e.get("event_type") == "question_answer" and e.get("answer_status") == "accepted"),
        "rejected_answers": sum(1 for e in events if e.get("event_type") == "question_answer" and e.get("answer_status") == "rejected"),
        "branch_decisions": sum(1 for e in events if e.get("event_type") == "branch_decision"),
        "gate_events": sum(1 for e in events if e.get("event_type") == "gate_check"),
        "system_actions": sum(1 for e in events if e.get("event_type") == "system_action"),
        "artifacts_created": sum(len(e.get("artifacts") or []) for e in events),
        "terminal_completion": any(e.get("event_type") == "terminal" and e.get("status") == "completed" for e in events),
    }


def _build_document(root: Path, events: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    started = events[0].get("timestamp_utc") if events else utc_now()
    terminal = next((e for e in reversed(events) if e.get("event_type") == "terminal"), None)
    status = str((terminal or {}).get("status") or "incomplete")
    final_state = next((e.get("state_after") for e in reversed(events) if e.get("state_after")), None)
    artifacts = []
    seen = set()
    for event in events:
        for artifact in event.get("artifacts") or []:
            key = artifact.get("path")
            if key not in seen:
                seen.add(key); artifacts.append(artifact)
    return {
        "schema": JOURNEY_SCHEMA,
        "playbook": _package_identity(root),
        "run": {
            "run_id": run_id,
            "started_at_utc": started,
            "ended_at_utc": (terminal or {}).get("timestamp_utc"),
            "status": status,
            "terminal_node": (terminal or {}).get("node_id"),
        },
        "events": events,
        "final_state": final_state or {},
        "artifacts": artifacts,
        "summary": _summary(events),
    }


def append_journey_event(root: str | Path, *, run_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    root_path = Path(root).resolve()
    events_path = root_path / EVENTS_PATH
    events_path.parent.mkdir(parents=True, exist_ok=True)
    previous = _load_events(root_path)
    sequence = len(previous) + 1
    previous_digest = str(previous[-1].get("event_digest") or "") if previous else ""
    event = copy.deepcopy(payload)
    event.update({
        "sequence": sequence,
        "timestamp_utc": event.get("timestamp_utc") or utc_now(),
        "event_type": event_type,
        "run_id": run_id,
        "previous_event_digest": previous_digest,
    })
    event["event_digest"] = _digest({k: v for k, v in event.items() if k != "event_digest"})
    with events_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush(); os.fsync(handle.fileno())
    events = previous + [event]
    document = _build_document(root_path, events, run_id)
    _atomic_write(root_path / JOURNEY_PATH, yaml.safe_dump(document, sort_keys=False, allow_unicode=True))
    return {"event": event, "events_path": EVENTS_PATH, "journey_path": JOURNEY_PATH, "journey_digest": _digest(document)}


def _question_id(root: Path, node: dict[str, Any]) -> str:
    node_id = str(node.get("id") or "UNKNOWN")
    declared = node.get("question_id")
    if declared:
        return str(declared)
    registry = root / "question_registry.json"
    if registry.exists():
        try:
            data = json.loads(registry.read_text(encoding="utf-8"))
            for item in data.get("questions", []):
                if str(item.get("node_id")) == node_id:
                    return str(item.get("question_id"))
        except Exception:
            pass
    return f"Q_{node_id}"


def record_intake_event(root: str | Path, *, run_id: str, node: dict[str, Any], answer: Any, status: str,
                        state_before: dict[str, Any], state_after: dict[str, Any], state_diff: dict[str, Any],
                        next_node: str | None, issues: list[dict[str, Any]], trace: dict[str, Any],
                        snapshot_path: str, snapshot_hash: str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    node_id = str(node.get("id") or "UNKNOWN")
    question_id = _question_id(root_path, node)
    accepted = status == "passed"
    event = {
        "node": {"id": node_id, "title": node.get("title") or node_id, "type": "user_intake"},
        "question": {"id": question_id, "text": node.get("question") or "", "language": node.get("question_language") or "und"},
        "answer": {"source": "human_user", "raw": answer, "structured": answer if isinstance(answer, (dict, list)) else None},
        "answer_status": "accepted" if accepted else "rejected",
        "normalization": {"accepted": accepted, "normalized_values": answer if accepted else None,
                          "validation_errors": issues if not accepted else []},
        "state_change": {"before_digest": _digest(state_before), "after_digest": _digest(state_after),
                         "changed_fields": state_diff if accepted else {}},
        "transition": {"current_node": node_id, "next_node": next_node or "", "branch_selected": next_node or None},
        "evidence": {"trace_seq": trace.get("step_index"), "trace_digest": trace.get("digest"),
                     "snapshot_path": snapshot_path, "snapshot_digest": snapshot_hash},
        "state_after": {"path": "runtime/live_session_state.json", "digest": _digest(state_after)},
    }
    return append_journey_event(root, run_id=run_id, event_type="question_answer", payload=event)


def finalize_journey(root: str | Path, *, run_id: str, status: str, node_id: str = "", reason: str = "") -> dict[str, Any]:
    return append_journey_event(root, run_id=run_id, event_type="terminal", payload={"status": status, "node_id": node_id, "reason": reason})


def validate_journey(root: str | Path, *, journey_path: str | Path | None = None) -> dict[str, Any]:
    root_path = Path(root).resolve()
    path = Path(journey_path).resolve() if journey_path else root_path / JOURNEY_PATH
    issues: list[dict[str, Any]] = []
    if not path.exists():
        return {"status": "failed", "schema": JOURNEY_SCHEMA, "issues": [{"code": "JOURNEY_MISSING", "message": str(path)}]}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    events = data.get("events") if isinstance(data, dict) else None
    if not isinstance(events, list):
        issues.append({"code": "JOURNEY_EVENTS_INVALID", "message": "events must be a list"}); events=[]
    previous = ""
    for expected, event in enumerate(events, 1):
        if event.get("sequence") != expected:
            issues.append({"code": "JOURNEY_SEQUENCE_GAP", "message": f"expected {expected}"})
        if event.get("previous_event_digest", "") != previous:
            issues.append({"code": "JOURNEY_CHAIN_INVALID", "message": f"sequence {expected}"})
        calculated = _digest({k: v for k, v in event.items() if k != "event_digest"})
        if event.get("event_digest") != calculated:
            issues.append({"code": "JOURNEY_EVENT_DIGEST_INVALID", "message": f"sequence {expected}"})
        previous = str(event.get("event_digest") or "")
        if event.get("event_type") == "question_answer":
            for key in ("node", "question", "answer", "answer_status", "state_change", "transition", "evidence"):
                if key not in event:
                    issues.append({"code": "JOURNEY_QA_FIELD_MISSING", "message": f"{key} at sequence {expected}"})
            if event.get("answer_status") == "rejected" and event.get("state_change", {}).get("changed_fields"):
                issues.append({"code": "JOURNEY_REJECTED_MUTATED_STATE", "message": f"sequence {expected}"})
    source_events = _load_events(root_path)
    if source_events != events:
        issues.append({"code": "JOURNEY_VIEW_DIVERGES_FROM_EVENTS", "message": "consolidated YAML differs from append-only event source"})
    report = {"status": "passed" if not issues else "failed", "schema": JOURNEY_SCHEMA,
              "journey_path": str(path.relative_to(root_path)), "event_count": len(events), "issues": issues}
    _atomic_write(root_path / VALIDATION_REPORT_PATH, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report
