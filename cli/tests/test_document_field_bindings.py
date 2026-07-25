from __future__ import annotations

import json
from pathlib import Path

import yaml

from ordo.document_field_bindings import validate_document_field_bindings


def write_case(tmp_path: Path, nodes: list[dict], schema: dict, field_spec: dict) -> dict:
    package = tmp_path / "package"
    (package / "source").mkdir(parents=True)
    (package / "source" / "program.ordo.yaml").write_text(
        yaml.safe_dump({"state": {"schema": schema}, "nodes": nodes}, sort_keys=False), encoding="utf-8"
    )
    bindings = tmp_path / "bindings.json"
    bindings.write_text(json.dumps({"documents": [{"document_id": "doc", "materialization_node": "MATERIALIZE", "required_fields": [field_spec]}]}), encoding="utf-8")
    return {"package": package, "bindings": bindings}


def test_document_field_binding_passes_when_required_field_is_collected(tmp_path: Path) -> None:
    case = write_case(
        tmp_path,
        [
            {"id": "START", "next": "COLLECT"},
            {"id": "COLLECT", "required_fields": ["title"], "on_answer": {"update_state": {"title": "$answer"}, "next": "MATERIALIZE"}},
            {"id": "MATERIALIZE"},
        ],
        {"title": None},
        {"field": "title", "required": True},
    )
    assert validate_document_field_bindings(**case)["status"] == "passed"


def test_document_field_binding_warns_when_collection_is_not_required(tmp_path: Path) -> None:
    case = write_case(
        tmp_path,
        [{"id": "START", "next": "COLLECT"}, {"id": "COLLECT", "on_answer": {"update_state": {"title": "$answer"}, "next": "MATERIALIZE"}}, {"id": "MATERIALIZE"}],
        {"title": None},
        {"field": "title", "required": True},
    )
    report = validate_document_field_bindings(**case)
    assert report["status"] == "passed_with_warnings"
    assert {item["code"] for item in report["warnings"]} == {"ORDO-DOC-FIELD-005"}


def test_document_field_binding_errors_when_no_producer_exists(tmp_path: Path) -> None:
    case = write_case(tmp_path, [{"id": "START", "next": "MATERIALIZE"}, {"id": "MATERIALIZE"}], {"title": None}, {"field": "title", "required": True})
    report = validate_document_field_bindings(**case)
    assert report["status"] == "failed"
    assert any(item["code"] == "ORDO-DOC-FIELD-003" for item in report["errors"])


def test_document_field_binding_errors_when_branch_does_not_collect_field(tmp_path: Path) -> None:
    case = write_case(
        tmp_path,
        [
            {"id": "START", "on_answer": {"next": "LEFT"}},
            {"id": "LEFT", "on_answer": {"update_state": {"title": "$answer"}, "next": "MATERIALIZE"}},
            {"id": "RIGHT", "next": "MATERIALIZE"},
            {"id": "MATERIALIZE"},
        ],
        {"title": None},
        {"field": "title", "required": True},
    )
    # Add a second root edge to exercise the all-path check.
    source = case["package"] / "source" / "program.ordo.yaml"
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    data["nodes"][0]["on_answer"] = {"next": "LEFT"}
    data["nodes"].insert(1, {"id": "START_RIGHT", "next": "RIGHT"})
    source.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    report = validate_document_field_bindings(**case)
    assert report["status"] == "failed"
    assert any(item["code"] == "ORDO-DOC-FIELD-004" for item in report["errors"])


def test_document_field_binding_errors_when_state_field_is_undeclared(tmp_path: Path) -> None:
    case = write_case(tmp_path, [{"id": "START", "next": "COLLECT"}, {"id": "COLLECT", "required_fields": ["title"], "on_answer": {"update_state": {"title": "$answer"}, "next": "MATERIALIZE"}}, {"id": "MATERIALIZE"}], {}, {"field": "title", "required": True})
    report = validate_document_field_bindings(**case)
    assert report["status"] == "failed"
    assert any(item["code"] == "ORDO-DOC-FIELD-002" for item in report["errors"])
