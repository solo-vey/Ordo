from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json

from ordo.execution_trace import (
    append_decision_interaction_event,
    finalize_execution_trace,
    initialize_execution_trace,
)
from ordo.replay_runner import export_replay_evidence, replay_recorded_run
from ordo.runtime_evidence import file_sha256

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "cli/tests/fixtures/clean_check/clean_minimal"


def _trace(tmp_path: Path) -> Path:
    source = PACKAGE / "source/program.ordo.yaml"
    policy = {
        "capture_level": "full",
        "replay": {
            "replayable": True,
            "replay_mode": "deterministic",
            "required_inputs_preserved": True,
            "external_dependencies": {"strategy": "recorded"},
        },
    }
    initialize_execution_trace(
        tmp_path,
        policy=policy,
        run_id="bl109",
        process_id="clean_minimal",
        process_version="1.0",
        execution_mode="test",
        entry_point="test",
        initial_state={"approved": False},
        playbook_identity={"source_path": "source/program.ordo.yaml", "sha256": "sha256:" + file_sha256(source), "version": "0.12"},
    )
    append_decision_interaction_event(
        tmp_path,
        policy=policy,
        actor={"actor_type": "analyst", "actor_id": "test"},
        node_id="N1",
        question_text="Continue?",
        analyst_response="yes",
        selected_transition="N2",
        decision_summary="Analyst accepted the recorded route.",
        state_before_ref="runtime/state_initial.json",
        state_after_ref="runtime/state_final.json",
        state_diff={"approved": {"before": False, "after": True}},
        replay_anchor="decision.bl109.n1",
    )
    finalize_execution_trace(tmp_path, policy=policy, status="completed", final_state={"approved": True})
    return tmp_path / "runtime/execution_trace.json"


def test_clean_checkout_replay_generates_machine_and_human_reports(tmp_path: Path, monkeypatch) -> None:
    trace = _trace(tmp_path)
    monkeypatch.setattr("ordo.replay_runner._git_clean", lambda _: (True, None))
    report_path = tmp_path / "report.json"
    report = replay_recorded_run(checkout=ROOT, package=PACKAGE, trace_path=trace, out=report_path)
    assert report["status"] == "passed"
    assert report["summary"]["evidence_classes"]["accepted_decision"] == 1
    assert report_path.is_file()
    assert report_path.with_suffix(".md").is_file()


def test_tampered_trace_is_rejected(tmp_path: Path, monkeypatch) -> None:
    trace = _trace(tmp_path)
    tampered = deepcopy(json.loads(trace.read_text(encoding="utf-8")))
    tampered["events"][1]["payload"]["decision_record"]["analyst_response"] = "no"
    trace.write_text(json.dumps(tampered), encoding="utf-8")
    monkeypatch.setattr("ordo.replay_runner._git_clean", lambda _: (True, None))
    report = replay_recorded_run(checkout=ROOT, package=PACKAGE, trace_path=trace, out=tmp_path / "report.json")
    assert report["status"] == "failed"
    assert any(item["code"] == "ORDO-EXEC-TRACE-005" for item in report["findings"])


def test_replay_evidence_export_proves_state_non_mutation(tmp_path: Path) -> None:
    trace = _trace(tmp_path)
    state = tmp_path / "state.json"
    state.write_text('{"active_node":"N1","checkpoint":"C1"}\n', encoding="utf-8")
    before = state.read_bytes()
    report = export_replay_evidence(trace_path=trace, state_path=state, out=tmp_path / "evidence")
    assert report["status"] == "passed"
    assert report["state_non_mutation"]["unchanged"] is True
    assert state.read_bytes() == before
    assert (tmp_path / "evidence/replay_evidence_export_report.md").is_file()
