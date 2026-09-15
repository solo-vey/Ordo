from __future__ import annotations

from copy import deepcopy

from ordo.compiler import compile_source
from ordo.linter import lint_source
from ordo.state_lineage import validate_state_lineage


def source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "example.lineage", "control_level": "standard", "execution_mode": "full_runtime"},
        "state": {"schema": {"title": "", "approved": False}},
        "nodes": [
            {
                "id": "N_COLLECT", "collection_mode": "analyst_answer", "required_fields": ["title"],
                "on_unmatched_input": {"action": "CLARIFY.REQUEST"},
                "on_answer": {"update_state": {"title": "$answer"}, "next": "N_REVIEW"},
            },
            {
                "id": "N_REVIEW", "collection_mode": "derived", "reads": ["title"],
                "on_unmatched_input": {"action": "CLARIFY.REQUEST"},
                "on_answer": {"update_state": {"approved": True}, "next": "G_READY"},
            },
        ],
        "gates": [{"id": "G_READY", "method": "mechanical", "trust_class": "deterministic", "condition": "state.approved is true", "on_pass": "END_DONE"}],
        "state_lineage": {
            "version": "1.0", "mode": "strict",
            "fields": [
                {"path": "title", "shape": "string", "owner": "N_COLLECT", "collection_mode": "analyst_answer", "consumers": ["N_REVIEW"], "registries": ["FIELD_REGISTRY"], "bindings": ["SUMMARY"]},
                {"path": "approved", "shape": "boolean", "owner": "N_REVIEW", "collection_mode": "derived", "consumers": ["G_READY"]},
            ],
            "registries": [{"id": "FIELD_REGISTRY", "fields": ["title"]}],
            "template_bindings": [{"id": "SUMMARY", "fields": ["title"]}],
        },
    }


def codes(report: dict) -> set[str]:
    return {item["code"] for item in report["issues"]}


def test_strict_state_lineage_closes_producers_consumers_bindings_and_conditions() -> None:
    report = validate_state_lineage(source())
    assert report["status"] == "passed", report
    assert report["summary"]["fields"] == 2
    assert next(field for field in report["fields"] if field["path"] == "title")["template_bindings"] == ["SUMMARY"]


def test_missing_state_lineage_declaration_and_missing_producer_fail_closed() -> None:
    value = source()
    value["state_lineage"]["fields"] = value["state_lineage"]["fields"][:1]
    report = validate_state_lineage(value)
    assert "STATE_LINEAGE_FIELD_UNOWNED" in codes(report)

    value = source()
    value["nodes"][0]["on_answer"] = {"next": "N_REVIEW"}
    report = validate_state_lineage(value)
    assert "STATE_LINEAGE_MISSING_PRODUCER" in codes(report)


def test_unowned_write_unused_collection_and_multiple_producers_are_detected() -> None:
    value = source()
    value["nodes"][0]["on_answer"]["update_state"]["unknown"] = "$answer"
    report = validate_state_lineage(value)
    assert "STATE_LINEAGE_WRITE_UNDECLARED" in codes(report)

    value = source()
    value["state_lineage"]["fields"][0]["consumers"] = []
    value["nodes"][1]["reads"] = []
    value["state_lineage"]["registries"] = []
    value["state_lineage"]["template_bindings"] = []
    report = validate_state_lineage(value)
    assert "STATE_LINEAGE_COLLECTED_UNUSED" in codes(report)

    value = source()
    value["nodes"][1]["on_answer"]["update_state"]["title"] = "duplicate"
    report = validate_state_lineage(value)
    assert "STATE_LINEAGE_MULTIPLE_OWNERS" in codes(report)


def test_shape_and_collection_mode_mismatches_are_detected() -> None:
    value = source()
    value["state_lineage"]["fields"][0]["shape"] = "array"
    value["nodes"][0]["collection_mode"] = "derived"
    report = validate_state_lineage(value)
    assert {"STATE_LINEAGE_SHAPE_MISMATCH", "STATE_LINEAGE_COLLECTION_MODE_MISMATCH"} <= codes(report)


def test_declared_registry_and_template_bindings_must_materialize() -> None:
    value = source()
    value["state_lineage"]["registries"] = []
    value["state_lineage"]["template_bindings"] = []
    report = validate_state_lineage(value)
    assert {"STATE_LINEAGE_REGISTRY_BINDING_MISSING", "STATE_LINEAGE_TEMPLATE_BINDING_MISSING"} <= codes(report)


def test_linter_and_compiler_integrate_state_lineage_contract() -> None:
    value = source()
    report = lint_source(value, {"test_cases": [{}]})
    assert report["state_lineage_validation"]["status"] == "passed", report
    ir = compile_source(deepcopy(value))
    op = next(item for item in ir["ops"] if item["op"] == "STATE.LINEAGE.DEF")
    assert op["mode"] == "strict"
