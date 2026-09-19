from __future__ import annotations

from copy import deepcopy

from ordo.compiler import compile_source
from ordo.linter import lint_source
from ordo.runner import apply_answers, initial_state
from ordo.value_provenance import evaluate_value_provenance, validate_value_provenance_contract


def source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "demo.provenance", "control_level": "standard", "execution_mode": "full_runtime"},
        "state": {"schema": {"risk_name": ""}},
        "nodes": [
            {"id": "N_COLLECT", "question": "Provide the risk name.", "allow_unmatched_input": True, "on_answer": {"update_state": {"risk_name": "$answer"}, "next": "N_CONFIRM"}},
            {"id": "N_CONFIRM", "question": "Confirm the proposed risk name.", "allow_unmatched_input": True, "on_answer": {"next": "N_DONE"}},
            {"id": "N_DONE", "terminal": True, "allow_unmatched_input": True},
        ],
        "value_provenance_contract": {
            "version": "1.0", "mode": "strict",
            "fields": [{
                "state_path": "risk_name",
                "allowed_provenance": ["analyst", "model_derived", "automatic", "default", "reference"],
                "reference_policy": "draft_only",
                "default_policy": "explicit_only",
                "confirmation_node": "N_CONFIRM",
            }],
        },
    }


def test_provenance_contract_round_trips_through_lint_compiler_and_runtime() -> None:
    value = source()
    report = validate_value_provenance_contract(value)
    assert report["status"] == "passed", report
    lint = lint_source(value, {"test_cases": []})
    assert lint["value_provenance_validation"]["status"] == "passed"
    ir = compile_source(deepcopy(value))
    assert next(op for op in ir["ops"] if op["op"] == "VALUE.PROVENANCE.CONTRACT.DEF")["version"] == "1.0"

    state = initial_state(value)
    events = apply_answers(value, state, {"N_COLLECT": {"value": "Counterparty concentration", "provenance": "analyst", "analyst_confirmed": True}})
    assert events[0]["type"] == "state_update"
    assert state["risk_name"] == "Counterparty concentration"
    assert state["_value_provenance"]["risk_name"] == {
        "value": "Counterparty concentration", "provenance": "analyst", "lifecycle": "confirmed", "analyst_confirmed": True,
    }


def test_reference_isolation_and_draft_rejection_do_not_mutate_state() -> None:
    value = source()
    node = value["nodes"][0]
    reference = evaluate_value_provenance(value, node, {"value": "Example risk", "provenance": "reference"})
    assert reference["status"] == "draft_confirmation_required"
    assert reference["next_node"] == "N_CONFIRM"
    assert reference["records"]["risk_name"]["lifecycle"] == "draft"
    assert reference["issues"][0]["code"] == "ORDO-PROVENANCE-REFERENCE-ISOLATED"

    state = initial_state(value)
    events = apply_answers(value, state, {"N_COLLECT": {"value": "Example risk", "provenance": "reference"}})
    assert events[0]["type"] == "draft_confirmation_required"
    assert events[0]["state_mutation"] is False
    assert events[0]["provenance_records"]["risk_name"]["lifecycle"] == "draft"
    assert state["risk_name"] == ""
    assert "_value_provenance" not in state


def test_unlabeled_default_and_unconfirmed_model_draft_fail_closed() -> None:
    value = source()
    node = value["nodes"][0]
    missing = evaluate_value_provenance(value, node, "silent default")
    assert missing["status"] == "provenance_required"
    model = evaluate_value_provenance(value, node, {"value": "Suggested risk", "provenance": "model_derived"})
    assert model["status"] == "draft_confirmation_required"
    assert model["records"]["risk_name"]["analyst_confirmed"] is False


def test_invalid_reference_policy_and_missing_confirmation_fail_validation() -> None:
    value = source()
    field = value["value_provenance_contract"]["fields"][0]
    field["reference_policy"] = "allow_default"
    field["confirmation_node"] = "N_MISSING"
    codes = {item["code"] for item in validate_value_provenance_contract(value)["issues"]}
    assert {"VALUE_PROVENANCE_REFERENCE_ISOLATION_REQUIRED", "VALUE_PROVENANCE_CONFIRMATION_NODE_REQUIRED"} <= codes
