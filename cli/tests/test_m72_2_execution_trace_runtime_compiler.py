from __future__ import annotations

from pathlib import Path
import json

import pytest

from ordo.compiler import compile_source
from ordo.execution_trace import (
    append_execution_trace_event,
    finalize_execution_trace,
    initialize_execution_trace,
    replay_plan,
    validate_execution_trace,
)


def source(capture_level: str = "standard") -> dict:
    return {
        "ordo": {"version": "0.12", "package": "test.trace", "control_level": "guided", "execution_mode": "normal"},
        "execution_trace": {"id": "TRACE", "capture_level": capture_level, "replay": {"replay_mode": "deterministic"}},
    }


def test_compiler_emits_normalized_execution_trace_def() -> None:
    ir = compile_source(source())
    op = next(x for x in ir["ops"] if x["op"] == "EXECUTION_TRACE.DEF")
    assert op["id"] == "test.trace.TRACE"
    assert op["capture_level"] == "standard"
    assert op["storage"] == {"format": "json", "path": "runtime/execution_trace.json", "append_only": True}
    assert op["replay"]["replay_mode"] == "deterministic"


def test_compiler_rejects_unknown_capture_level() -> None:
    with pytest.raises(ValueError):
        compile_source(source("verbose"))


def test_runtime_trace_lifecycle_integrity_and_terminal_lock(tmp_path: Path) -> None:
    policy = source()["execution_trace"]
    initialize_execution_trace(tmp_path, policy=policy, run_id="r1", process_id="p1", process_version="1", execution_mode="normal", entry_point="start")
    append_execution_trace_event(tmp_path, policy=policy, event_type="user_input", actor={"actor_type": "analyst"}, payload={"answer": "yes", "token": "secret"}, outcome={"status": "accepted"})
    trace = finalize_execution_trace(tmp_path, policy=policy, status="completed", final_state={"snapshot_ref": "s1", "result": "ok"})
    assert validate_execution_trace(trace)["valid"] is True
    assert trace["events"][1]["payload"]["token"] == {"value_redacted": True}
    assert trace["events"][-1]["event_type"] == "run_completed"
    with pytest.raises(RuntimeError):
        append_execution_trace_event(tmp_path, policy=policy, event_type="warning_raised", actor={"actor_type": "runtime"})


def test_minimal_capture_filters_user_input(tmp_path: Path) -> None:
    policy = source("minimal")["execution_trace"]
    initialize_execution_trace(tmp_path, policy=policy, run_id="r2", process_id="p", process_version="1", execution_mode="normal", entry_point="start")
    result = append_execution_trace_event(tmp_path, policy=policy, event_type="user_input", actor={"actor_type": "user"}, payload={"answer": "x"})
    assert result == {"captured": False, "reason": "capture_level_filtered", "event_type": "user_input"}


def test_replay_plan_modes(tmp_path: Path) -> None:
    policy = source()["execution_trace"]
    initialize_execution_trace(tmp_path, policy=policy, run_id="r3", process_id="p", process_version="1", execution_mode="normal", entry_point="start")
    append_execution_trace_event(tmp_path, policy=policy, event_type="user_input", actor={"actor_type": "user"}, payload={"field": "x", "value": 1}, outcome={"status": "accepted"})
    trace = finalize_execution_trace(tmp_path, policy=policy, status="completed")
    plan = replay_plan(trace, mode="simulation")
    assert plan["ready"] is True
    assert any(step["event_type"] == "user_input" for step in plan["steps"])
    assert all(step["side_effects_allowed"] is False for step in plan["steps"])


def test_persisted_file_is_json(tmp_path: Path) -> None:
    policy = source()["execution_trace"]
    initialize_execution_trace(tmp_path, policy=policy, run_id="r4", process_id="p", process_version="1", execution_mode="normal", entry_point="start")
    data = json.loads((tmp_path / "runtime/execution_trace.json").read_text(encoding="utf-8"))
    assert data["trace_format"] == "ordo-execution-trace.v1"
