from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml

from ordo.compiler import compile_source
from ordo.cross_artifact_contract import validate_cross_artifact_contract


def source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "example.cross_artifact", "control_level": "standard", "execution_mode": "full_runtime"},
        "state": {"schema": {"customer_name": "", "final_status": "", "metadata_version": ""}},
        "nodes": [
            {"id": "N_FINALIZE", "question": "Finalize.", "on_unmatched_input": {"action": "CLARIFY.REQUEST"}, "on_answer": {"update_state": {"final_status": "ready", "metadata_version": "v1"}, "next": "END_DONE"}},
        ],
        "cross_artifact_contract": {
            "version": "1.0",
            "mode": "strict",
            "documents": [
                {
                    "id": "SUMMARY",
                    "template": "templates/summary.md",
                    "bindings": {"customer_name": "state.customer_name"},
                    "validator": {"expected_headings": ["customer-details"]},
                    "finalization": {
                        "node": "N_FINALIZE",
                        "writes": ["state.final_status", "state.metadata_version"],
                        "rendered_artifact": "rendered/summary.md",
                        "rendered_fields": ["customer_name", "final_status", "metadata_version"],
                    },
                }
            ],
        },
    }


def write_case(root: Path, value: dict | None = None) -> dict:
    value = value or source()
    (root / "templates").mkdir(parents=True)
    (root / "rendered").mkdir()
    (root / "templates" / "summary.md").write_text("# Customer Details\n\n{{customer_name}}\n", encoding="utf-8")
    (root / "rendered" / "summary.md").write_text("# Customer Details\n\nAcme\nStatus: ready\nVersion: v1\n", encoding="utf-8")
    (root / "state.yaml").write_text(yaml.safe_dump({"customer_name": "Acme", "final_status": "ready", "metadata_version": "v1"}), encoding="utf-8")
    return value


def codes(report: dict) -> set[str]:
    return {item["code"] for item in report["issues"]}


def test_symmetric_headings_bindings_finalization_and_semantic_rendering_pass(tmp_path: Path) -> None:
    value = write_case(tmp_path)
    report = validate_cross_artifact_contract(tmp_path, value, state_path=tmp_path / "state.yaml")
    assert report["status"] == "passed", report
    assert report["documents"][0]["checks"][0]["missing"] == []


def test_missing_heading_and_unbound_placeholder_identify_owner_layer(tmp_path: Path) -> None:
    value = source()
    value["cross_artifact_contract"]["documents"][0]["validator"]["expected_headings"] = ["Required Summary"]
    value["cross_artifact_contract"]["documents"][0]["bindings"] = {}
    write_case(tmp_path, value)
    report = validate_cross_artifact_contract(tmp_path, value, state_path=tmp_path / "state.yaml")
    assert {"XAC-HEADINGS-001", "XAC-HEADINGS-002", "XAC-BINDING-001"} <= codes(report)
    assert {item["owner_layer"] for item in report["issues"]} >= {"validator", "template", "binding"}


def test_unknown_binding_and_finalization_rendered_mismatch_fail_closed(tmp_path: Path) -> None:
    value = source()
    document = value["cross_artifact_contract"]["documents"][0]
    document["bindings"] = {"customer_name": "state.unknown"}
    document["finalization"]["writes"] = ["state.unknown"]
    (tmp_path / "templates").mkdir(parents=True)
    (tmp_path / "rendered").mkdir()
    (tmp_path / "templates" / "summary.md").write_text("# Customer Details\n{{customer_name}}", encoding="utf-8")
    (tmp_path / "rendered" / "summary.md").write_text("# Customer Details\nOther", encoding="utf-8")
    (tmp_path / "state.yaml").write_text(yaml.safe_dump({"customer_name": "Acme", "final_status": "ready", "metadata_version": "v1"}), encoding="utf-8")
    report = validate_cross_artifact_contract(tmp_path, value, state_path=tmp_path / "state.yaml")
    assert {"XAC-BINDING-002", "XAC-FINALIZATION-001", "XAC-RENDERED-002"} <= codes(report)


def test_compiler_preserves_cross_artifact_contract() -> None:
    ir = compile_source(deepcopy(source()))
    op = next(item for item in ir["ops"] if item["op"] == "CROSS.ARTIFACT.CONTRACT.DEF")
    assert op["documents"][0]["id"] == "SUMMARY"
