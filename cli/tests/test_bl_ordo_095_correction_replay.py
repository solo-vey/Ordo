from __future__ import annotations

from copy import deepcopy

from ordo.compiler import compile_source
from ordo.correction_replay import plan_correction, validate_correction_contract
from ordo.linter import lint_source


def source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "example.correction", "control_level": "standard", "execution_mode": "full_runtime"},
        "state": {"schema": {"source_value": "", "derived_score": 0, "unrelated_confirmation": False}},
        "nodes": [
            {"id": "N_SOURCE", "on_unmatched_input": {"action": "CLARIFY.REQUEST"}},
            {"id": "N_DERIVE", "on_unmatched_input": {"action": "CLARIFY.REQUEST"}},
        ],
        "gates": [{"id": "G_READY", "method": "mechanical", "trust_class": "deterministic", "condition": "state.derived_score > 0", "on_pass": "END"}],
        "artifacts": [{"id": "A_SUMMARY"}],
        "correction_contract": {"version": "1.0", "mode": "strict", "rules": [{"source": "source_value", "invalidate": {"state": ["derived_score"], "derivations": ["N_DERIVE"], "gates": ["G_READY"], "tests": ["TC_SCORE"], "artifacts": ["A_SUMMARY"]}, "replay": {"gates": ["G_READY"]}}]},
    }


def case_catalog() -> dict:
    return {"test_cases": [{"id": "TC_SCORE"}]}


def codes(report: dict) -> set[str]:
    return {item["code"] for item in report["issues"]}


def test_contract_closes_dependencies_and_compiles() -> None:
    report = validate_correction_contract(source(), case_catalog())
    assert report["status"] == "passed", report
    assert lint_source(source(), case_catalog())["correction_contract_validation"]["status"] == "passed"
    op = next(item for item in compile_source(deepcopy(source()))["ops"] if item["op"] == "CORRECTION.CONTRACT.DEF")
    assert op["version"] == "1.0"


def test_correction_invalidates_only_declared_downstream_state_and_replays_gate() -> None:
    state = {"source_value": "old", "derived_score": 7, "unrelated_confirmation": True}
    report = plan_correction(source(), state, path="source_value", value="new", tests=case_catalog())
    assert report["status"] == "planned", report
    assert state == {"source_value": "old", "derived_score": 7, "unrelated_confirmation": True}
    assert report["corrected_state"] == {"source_value": "new", "derived_score": None, "unrelated_confirmation": True}
    assert report["invalidation"]["state"][0]["path"] == "derived_score"
    assert report["gate_replay"][0]["id"] == "G_READY"
    assert report["gate_replay"][0]["status"] == "blocked"


def test_unknown_or_unsafe_dependencies_fail_closed() -> None:
    value = source()
    value["correction_contract"]["rules"][0]["invalidate"]["state"] = ["source_value"]
    value["correction_contract"]["rules"][0]["replay"]["gates"] = []
    assert {"CORRECTION_INVALIDATED_STATE_UNKNOWN", "CORRECTION_REPLAY_GATE_REQUIRED"} <= codes(validate_correction_contract(value, case_catalog()))
    report = plan_correction(source(), {}, path="unrelated_confirmation", value=True, tests=case_catalog())
    assert report["status"] == "blocked"
