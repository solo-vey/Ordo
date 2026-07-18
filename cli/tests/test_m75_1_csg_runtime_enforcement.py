from __future__ import annotations

import json
from pathlib import Path

import pytest

from ordo.csg_runtime import enforce_csg_proposal
from ordo.runner import run_package


CSG = {
    "supported": True,
    "enabled": True,
    "mode": "guided_redirect",
    "state_change_on_out_of_scope": False,
}


@pytest.mark.parametrize("classification", [
    "clarification", "process_meta_question", "related_context",
    "unrelated_topic", "unclassifiable_input",
])
def test_non_mutating_deviation_blocks_protected_state_change(classification):
    state = {"current_node": "N2", "confirmed": {"alias": True}}
    before = json.loads(json.dumps(state))
    result = enforce_csg_proposal(CSG, state, {
        "classification": classification,
        "action": "bad_mutation",
        "state_update": {"confirmed.alias": False},
        "target_node": "N9",
    })
    assert result["status"] == "blocked"
    assert state == before
    assert result["issues"][0]["code"] == "CSG_PROTECTED_STATE_MUTATION_BLOCKED"


@pytest.mark.parametrize("classification", [
    "answer_to_active_question", "correction", "backtrack_request", "requirement_change",
])
def test_authorized_classes_can_apply_explicit_state_update(classification):
    state = {"current_node": "N2", "value": "old"}
    result = enforce_csg_proposal(CSG, state, {
        "classification": classification,
        "action": "apply",
        "state_update": {"value": "new"},
        "target_node": "N1",
    })
    assert result["status"] == "applied"
    assert state["value"] == "new"
    assert state["current_node"] == "N1"


def test_pause_resume_preserves_and_restores_node_without_business_state_mutation():
    state = {"current_node": "N5", "contract": {"alias": "A"}}
    paused = enforce_csg_proposal(CSG, state, {"classification": "pause_request", "action": "pause_process"})
    assert paused["status"] == "applied"
    assert state["_csg_runtime"]["status"] == "paused"
    assert state["_csg_runtime"]["suspended_node"] == "N5"
    assert state["contract"] == {"alias": "A"}

    blocked = enforce_csg_proposal(CSG, state, {
        "classification": "answer_to_active_question", "action": "accept_answer",
        "state_update": {"contract.alias": "B"},
    })
    assert blocked["status"] == "blocked"
    assert state["contract"]["alias"] == "A"

    resumed = enforce_csg_proposal(CSG, state, {"classification": "resume_request", "action": "resume_process"})
    assert resumed["status"] == "applied"
    assert state["current_node"] == "N5"
    assert state["_csg_runtime"]["status"] == "active"


def test_exit_blocks_following_proposals_and_marks_incomplete():
    state = {"current_node": "N3", "blocked": False}
    exited = enforce_csg_proposal(CSG, state, {"classification": "exit_request", "action": "exit_process"})
    assert exited["status"] == "applied"
    assert state["blocked"] is True
    assert state["go_no_go"] == "incomplete"
    follow = enforce_csg_proposal(CSG, state, {"classification": "clarification", "action": "clarify_active_step"})
    assert follow["status"] == "blocked"
    assert follow["issues"][0]["code"] == "CSG_PROCESS_EXITED"


def test_safety_bypass_allows_response_but_never_state_mutation():
    state = {"current_node": "N3", "answer": None}
    ok = enforce_csg_proposal(CSG, state, {
        "classification": "unsafe_or_emergency_message", "action": "bypass_for_safety"
    })
    assert ok["status"] == "applied"
    assert any(e["type"] == "conversation.scope_guard.bypassed_for_safety" for e in ok["events"])

    before = json.loads(json.dumps(state))
    blocked = enforce_csg_proposal(CSG, state, {
        "classification": "unsafe_or_emergency_message", "action": "bypass_for_safety",
        "state_update": {"answer": "invented"},
    })
    assert blocked["status"] == "blocked"
    assert state == before


def test_run_package_enforces_csg_events_and_records_trace(tmp_path: Path):
    package = tmp_path / "pkg"
    (package / "source").mkdir(parents=True)
    (package / "tests").mkdir()
    (package / "tests" / "tests.yaml").write_text("tests: []\n", encoding="utf-8")
    (package / "reports").mkdir()
    (package / "runtime").mkdir()
    (package / "ordo.yml").write_text(
        "name: csg-test\nversion: 1.0\nsource: source/program.ordo.yaml\ntests: tests/tests.yaml\n",
        encoding="utf-8",
    )
    (package / "source" / "program.ordo.yaml").write_text(
        """ordo:\n  version: '0.12'\n  package: csg-test\nconversation_scope_guard:\n  id: CSG\n  supported: true\n  enabled: true\n  mode: guided_redirect\n  scope: current_process\n  out_of_scope_behavior: redirect\n  state_change_on_out_of_scope: false\n  escalation: {}\n  trace: {}\nstate:\n  id: S\n  schema:\n    current_node: N1\n    alias: KEEP\nnodes: []\ngates: []\nassertions: []\noutputs: []\n""",
        encoding="utf-8",
    )
    events = tmp_path / "events.json"
    events.write_text(json.dumps([
        {
            "classification": "unrelated_topic",
            "action": "redirect",
            "state_update": {"alias": "CORRUPTED"},
        },
        {"classification": "pause_request", "action": "pause_process"},
    ]), encoding="utf-8")

    report = run_package(package, csg_events_path=events)
    assert report["state"]["final"]["alias"] == "KEEP"
    assert report["csg_report"][0]["status"] == "blocked"
    assert report["csg_report"][1]["status"] == "applied"
    assert any(e["type"] == "runner.action.blocked" for e in report["events"])
    assert any(e["type"] == "process.paused" for e in report["events"])
