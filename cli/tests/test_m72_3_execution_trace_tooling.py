from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json

import pytest
import yaml

from ordo.execution_trace import (
    append_execution_trace_event,
    canonical_checksum,
    finalize_execution_trace,
    initialize_execution_trace,
    replay_plan,
    validate_execution_trace,
)

ROOT = Path(__file__).resolve().parents[2]


def _policy(level: str = "standard", replayable: bool = True) -> dict:
    return {
        "id": "TRACE",
        "capture_level": level,
        "replay": {
            "replayable": replayable,
            "replay_mode": "deterministic",
            "required_inputs_preserved": replayable,
        },
    }


@pytest.mark.parametrize(
    "name",
    ["execution_trace_full.yaml", "execution_trace_minimal.yaml", "execution_trace_replayable.yaml"],
)
def test_canonical_examples_parse_and_have_consistent_event_counts(name: str) -> None:
    data = yaml.safe_load((ROOT / "language/examples" / name).read_text(encoding="utf-8"))
    trace = data["execution_trace"]
    assert trace["integrity"]["event_count"] == len(trace["events"])
    assert [e["sequence"] for e in trace["events"]] == list(range(1, len(trace["events"]) + 1))


def test_integrity_detects_event_count_and_sequence_tampering(tmp_path: Path) -> None:
    policy = _policy()
    initialize_execution_trace(
        tmp_path,
        policy=policy,
        run_id="tamper",
        process_id="demo",
        process_version="1",
        execution_mode="normal",
        entry_point="start",
    )
    append_execution_trace_event(
        tmp_path,
        policy=policy,
        event_type="gate_passed",
        actor={"actor_type": "runtime"},
        payload={"gate_id": "g1"},
        outcome={"status": "passed"},
    )
    trace = finalize_execution_trace(tmp_path, policy=policy, status="completed")
    assert validate_execution_trace(trace)["valid"] is True

    count_tampered = deepcopy(trace)
    count_tampered["integrity"]["event_count"] += 1
    assert validate_execution_trace(count_tampered)["valid"] is False

    sequence_tampered = deepcopy(trace)
    sequence_tampered["events"][1]["sequence"] = 99
    assert validate_execution_trace(sequence_tampered)["valid"] is False


def test_checksum_is_stable_and_detects_payload_change(tmp_path: Path) -> None:
    policy = _policy()
    initialize_execution_trace(
        tmp_path,
        policy=policy,
        run_id="checksum",
        process_id="demo",
        process_version="1",
        execution_mode="normal",
        entry_point="start",
    )
    append_execution_trace_event(
        tmp_path,
        policy=policy,
        event_type="user_input",
        actor={"actor_type": "user"},
        payload={"field": "x", "value": 1},
        outcome={"status": "accepted"},
    )
    trace = finalize_execution_trace(tmp_path, policy=policy, status="completed")
    checksum = trace["integrity"]["checksum"]
    assert checksum.startswith("sha256:")

    changed = deepcopy(trace)
    changed["events"][1]["payload"]["value"] = 2
    without_checksum = deepcopy(changed)
    without_checksum["integrity"]["checksum"] = None
    assert canonical_checksum(without_checksum) != checksum


def test_all_replay_modes_apply_expected_side_effect_policy(tmp_path: Path) -> None:
    policy = _policy()
    initialize_execution_trace(
        tmp_path,
        policy=policy,
        run_id="replay",
        process_id="demo",
        process_version="1",
        execution_mode="normal",
        entry_point="start",
    )
    append_execution_trace_event(
        tmp_path,
        policy=policy,
        event_type="user_input",
        actor={"actor_type": "service"},
        payload={"operation": "create"},
        outcome={"status": "completed"},
    )
    trace = finalize_execution_trace(tmp_path, policy=policy, status="completed")

    deterministic = replay_plan(trace, mode="deterministic")
    reevaluate = replay_plan(trace, mode="re_evaluate")
    simulation = replay_plan(trace, mode="simulation")
    audit = replay_plan(trace, mode="audit_only")

    assert deterministic["ready"] is True
    assert reevaluate["ready"] is True
    assert simulation["ready"] is True
    assert audit["ready"] is True
    assert any(step["side_effects_allowed"] for step in deterministic["steps"])
    assert all(not step["side_effects_allowed"] for step in simulation["steps"])
    assert all(not step["side_effects_allowed"] for step in audit["steps"])


def test_persisted_trace_never_contains_plain_sensitive_values(tmp_path: Path) -> None:
    policy = _policy()
    initialize_execution_trace(
        tmp_path,
        policy=policy,
        run_id="redaction",
        process_id="demo",
        process_version="1",
        execution_mode="normal",
        entry_point="start",
    )
    append_execution_trace_event(
        tmp_path,
        policy=policy,
        event_type="user_input",
        actor={"actor_type": "user"},
        payload={"token": "top-secret", "nested": {"password": "hidden"}},
        outcome={"status": "accepted"},
    )
    raw = (tmp_path / "runtime/execution_trace.json").read_text(encoding="utf-8")
    assert "top-secret" not in raw
    assert "hidden" not in raw
    data = json.loads(raw)
    assert data["events"][1]["payload"]["token"] == {"value_redacted": True}
