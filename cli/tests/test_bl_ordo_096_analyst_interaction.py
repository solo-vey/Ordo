from __future__ import annotations

from copy import deepcopy

from ordo.analyst_interaction import (
    describe_gate_failure,
    evaluate_analyst_submission,
    route_side_question,
    validate_analyst_interaction_contract,
)
from ordo.compiler import compile_source
from ordo.linter import lint_source


def source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "demo.interaction", "control_level": "standard", "execution_mode": "full_runtime"},
        "state": {"schema": {"summary": "", "profile": {}}},
        "nodes": [
            {"id": "N_FREE_TEXT", "question": "Describe the objective.", "on_answer": {"update_state": {"summary": "$answer"}, "next": "N_STRUCTURED"}},
            {"id": "N_RETRY_TEXT", "question": "Provide a meaningful objective.", "on_answer": {"next": "N_FREE_TEXT"}},
            {"id": "N_STRUCTURED", "question": "Provide profile fields.", "on_answer": {"update_state": {"profile": "$answer"}, "next": "N_CONFIRM"}},
            {"id": "N_RETRY_PROFILE", "question": "Provide all required profile fields.", "on_answer": {"next": "N_STRUCTURED"}},
            {"id": "N_CONFIRM", "question": "Confirm the draft.", "on_answer": {"next": "N_DONE"}},
            {"id": "N_DONE", "terminal": True},
        ],
        "gates": [{"id": "G_PROFILE_READY", "condition": "state.profile is not empty"}],
        "analyst_interaction_contract": {
            "version": "1.0", "mode": "strict", "side_question_policy": "return_to_active_node",
            "interactions": [
                {"node": "N_FREE_TEXT", "field_meaning": "A concise analyst-owned statement of the objective.", "response_mode": "free_text", "semantic_sufficiency": {"required": True, "min_length": 8}, "on_rejected_semantics": "N_RETRY_TEXT"},
                {"node": "N_STRUCTURED", "field_meaning": "A structured profile with an owner and an identifier.", "response_mode": "structured", "semantic_sufficiency": {"required": True, "required_keys": ["owner", "identifier"]}, "on_rejected_semantics": "N_RETRY_PROFILE", "draft_confirmation": {"required": True, "confirmation_node": "N_CONFIRM"}},
            ],
            "gate_failures": [{"gate": "G_PROFILE_READY", "message": "The profile is incomplete.", "remedy": "Provide both owner and identifier.", "retry_node": "N_RETRY_PROFILE"}],
            "route_labels": [{"from": "N_STRUCTURED", "to": "N_CONFIRM", "label": "Review structured draft"}],
        },
    }


def test_contract_covers_human_facing_meaning_modes_routes_and_compilation() -> None:
    value = source()
    report = validate_analyst_interaction_contract(value)
    assert report["status"] == "passed", report
    lint = lint_source(value, {"test_cases": []})
    assert lint["analyst_interaction_validation"]["status"] == "passed"
    ir = compile_source(deepcopy(value))
    contract = next(op for op in ir["ops"] if op["op"] == "ANALYST.INTERACTION.CONTRACT.DEF")
    assert contract["side_question_policy"] == "return_to_active_node"


def test_conversation_fixtures_reject_semantics_and_preserve_partial_retry() -> None:
    value = source()
    text = value["nodes"][0]
    rejected = evaluate_analyst_submission(value, text, "short")
    assert rejected["status"] == "semantic_rejected"
    assert rejected["next_node"] == "N_RETRY_TEXT"
    assert evaluate_analyst_submission(value, text, "A sufficiently detailed objective.")["status"] == "passed"

    structured = value["nodes"][2]
    partial = evaluate_analyst_submission(value, structured, {"owner": "analyst"})
    assert partial["status"] == "semantic_rejected"
    assert partial["next_node"] == "N_RETRY_PROFILE"
    unconfirmed = evaluate_analyst_submission(value, structured, {"value": {"owner": "analyst", "identifier": "PF-1"}})
    assert unconfirmed["status"] == "draft_confirmation_required"
    assert unconfirmed["next_node"] == "N_CONFIRM"
    confirmed = evaluate_analyst_submission(value, structured, {"value": {"owner": "analyst", "identifier": "PF-1"}, "draft_confirmed": True})
    assert confirmed["status"] == "passed"


def test_side_question_is_explicitly_non_mutating_and_returns_to_active_node() -> None:
    report = route_side_question(source(), active_node="N_STRUCTURED", question="Why is this field required?")
    assert report["status"] == "resumed"
    assert report["next_node"] == "N_STRUCTURED"
    assert report["state_mutation"] is False
    gate = describe_gate_failure(source(), "G_PROFILE_READY")
    assert gate == {"status": "actionable", "gate": "G_PROFILE_READY", "message": "The profile is incomplete.", "remedy": "Provide both owner and identifier.", "retry_node": "N_RETRY_PROFILE"}


def test_invalid_contract_fails_closed() -> None:
    value = source()
    value["analyst_interaction_contract"]["interactions"][0]["on_rejected_semantics"] = "N_UNKNOWN"
    value["analyst_interaction_contract"]["interactions"][1]["draft_confirmation"]["confirmation_node"] = "N_UNKNOWN"
    codes = {issue["code"] for issue in validate_analyst_interaction_contract(value)["issues"]}
    assert {"ANALYST_INTERACTION_RETRY_ROUTE_REQUIRED", "ANALYST_INTERACTION_DRAFT_CONFIRMATION_ROUTE_REQUIRED"} <= codes
