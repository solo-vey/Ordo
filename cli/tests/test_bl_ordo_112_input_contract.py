from __future__ import annotations

from copy import deepcopy

from ordo.compiler import compile_source
from ordo.input_contract import evaluate_input_submission, validate_input_contract
from ordo.linter import lint_source
from ordo.runner import apply_answers, initial_state


def source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "example.inputs", "control_level": "standard", "execution_mode": "full_runtime"},
        "state": {"schema": {"customer_name": "", "approved": False}},
        "nodes": [
            {
                "id": "N_COLLECT_NAME",
                "question": "Provide the customer name.",
                "collection_mode": "analyst_answer",
                "on_unmatched_input": {"action": "CLARIFY.REQUEST"},
                "on_answer": {"update_state": {"customer_name": "$answer"}, "next": "N_REVIEW"},
                "input_contract": {"state_writes": {"customer_name": "CUSTOMER_NAME"}},
            },
            {
                "id": "N_CLARIFY_NAME",
                "question": "Clarify the customer name.",
                "on_unmatched_input": {"action": "CLARIFY.REQUEST"},
                "on_answer": {"next": "N_COLLECT_NAME"},
            },
            {
                "id": "N_REVIEW",
                "question": "Confirm the name.",
                "on_unmatched_input": {"action": "CLARIFY.REQUEST"},
                "on_answer": {"next": "END_DONE"},
            },
        ],
        "input_contract": {
            "version": "1.0",
            "mode": "strict",
            "inputs": [
                {
                    "id": "CUSTOMER_NAME",
                    "state_path": "customer_name",
                    "shape": "string",
                    "required": True,
                    "responsible_node": "N_COLLECT_NAME",
                    "missing_route": "N_COLLECT_NAME",
                    "ambiguity": {"policy": "clarify", "clarification_node": "N_CLARIFY_NAME"},
                }
            ],
        },
    }


def codes(report: dict) -> set[str]:
    return {item["code"] for item in report["issues"]}


def test_required_input_contract_is_closed_and_reported() -> None:
    report = validate_input_contract(source())
    assert report["status"] == "passed", report
    assert report["inputs"] == [{"id": "CUSTOMER_NAME", "expected_state_contract": "CUSTOMER_NAME", "state_path": "customer_name", "responsible_node": "N_COLLECT_NAME", "required": True, "status": "ok"}]


def test_missing_required_input_and_ambiguous_concept_route_without_mutation() -> None:
    value = source()
    node = value["nodes"][0]
    missing = evaluate_input_submission(value, node, "")
    assert missing["status"] == "missing_required"
    assert missing["next_node"] == "N_COLLECT_NAME"
    ambiguous = evaluate_input_submission(value, node, {"value": "Acme", "concept": "CUSTOMER_NAME", "ambiguous": True})
    assert ambiguous["status"] == "clarification_required"
    assert ambiguous["next_node"] == "N_CLARIFY_NAME"


def test_incompatible_concept_and_silent_mapping_are_rejected() -> None:
    value = source()
    node = value["nodes"][0]
    state = initial_state(value)
    events = apply_answers(value, state, {"N_COLLECT_NAME": {"value": "Acme", "concept": "ACCOUNT_ID"}})
    assert events[0]["type"] == "input_rejected"
    assert state["customer_name"] == ""

    value = source()
    del value["nodes"][0]["input_contract"]
    report = validate_input_contract(value)
    assert {"INPUT_CONTRACT_WRITE_BINDING_MISSING", "INPUT_CONTRACT_SILENT_STATE_MAPPING"} <= codes(report)


def test_invalid_missing_and_clarification_routes_fail_closed() -> None:
    value = source()
    value["input_contract"]["inputs"][0]["missing_route"] = "N_UNKNOWN"
    value["input_contract"]["inputs"][0]["ambiguity"]["clarification_node"] = "N_UNKNOWN"
    report = validate_input_contract(value)
    assert {"INPUT_CONTRACT_MISSING_ROUTE_REQUIRED", "INPUT_CONTRACT_CLARIFICATION_ROUTE_REQUIRED"} <= codes(report)


def test_linter_and_compiler_preserve_input_contract() -> None:
    value = source()
    report = lint_source(value, {"test_cases": [{}]})
    assert report["input_contract_validation"]["status"] == "passed", report
    ir = compile_source(deepcopy(value))
    contract = next(op for op in ir["ops"] if op["op"] == "INPUT.CONTRACT.DEF")
    node = next(op for op in ir["ops"] if op["op"] == "NODE.DEF" and op.get("source_local_id") == "N_COLLECT_NAME")
    assert contract["mode"] == "strict"
    assert node["input_contract"]["state_writes"]["customer_name"] == "CUSTOMER_NAME"
