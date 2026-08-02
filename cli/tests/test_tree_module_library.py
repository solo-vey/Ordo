from __future__ import annotations

from pathlib import Path
import tempfile

import yaml

from ordo.tree_modules import diff_instance, instantiate_template, list_templates, validate_instance


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "packages" / "ordo_applied_project_factory"


def _host(path: Path) -> Path:
    source = {
        "state": {"schema": {"existing_field": None}},
        "nodes": [{"id": "N_ENTRY"}, {"id": "N_EXIT"}],
        "gates": [{"id": "G_EXISTING"}],
    }
    path.write_text(yaml.safe_dump(source), encoding="utf-8")
    return path


def _params(path: Path, prefix: str = "DOC") -> Path:
    path.write_text(yaml.safe_dump({"params": {
        "instance_id": "sample_document",
        "id_prefix": prefix,
        "document_title": "Sample document",
        "required_fields": ["title", "owner"],
        "entry_node": "N_ENTRY",
        "success_exit_node": "N_EXIT",
    }}), encoding="utf-8")
    return path


def test_library_catalog_exposes_three_reusable_templates():
    report = list_templates(PACKAGE)
    assert report["status"] == "passed"
    assert {entry["id"] for entry in report["templates"]} == {
        "DOCUMENT_MATERIALIZATION_LIFECYCLE", "PACKAGE_HANDOFF_LIFECYCLE",
        "IMPLEMENTATION_CHANGE_LIFECYCLE",
    }


def test_implementation_change_instance_is_domain_neutral_and_validates():
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        host = _host(work / "host.yaml")
        params = work / "params.yaml"
        params.write_text(yaml.safe_dump({"params": {
            "instance_id": "application_implementation",
            "id_prefix": "APPIMPL",
            "module_title": "application capability implementation module",
            "implementation_prompt_field": "implementation_prompt_path",
            "confirmed_requirements_fields": ["approved_requirements_path"],
            "entry_node": "N_ENTRY",
            "success_exit_node": "N_EXIT",
        }}), encoding="utf-8")
        report = instantiate_template(PACKAGE, "IMPLEMENTATION_CHANGE_LIFECYCLE", params, work / "instance.yaml", host)
        assert report["status"] == "passed"
        assert validate_instance(work / "instance.yaml", host)["status"] == "passed"


def test_document_instance_is_deterministic_and_validates_against_host():
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        host = _host(work / "host.yaml")
        params = _params(work / "params.yaml")
        first = instantiate_template(PACKAGE, "DOCUMENT_MATERIALIZATION_LIFECYCLE", params, work / "one.yaml", host)
        second = instantiate_template(PACKAGE, "DOCUMENT_MATERIALIZATION_LIFECYCLE", params, work / "two.yaml", host)
        assert first["status"] == second["status"] == "passed"
        assert first["instance"]["provenance"]["generated_fragment_sha256"] == second["instance"]["provenance"]["generated_fragment_sha256"]
        assert validate_instance(work / "one.yaml", host)["status"] == "passed"
        assert diff_instance(PACKAGE, work / "one.yaml") == {
            "status": "passed",
            "template_id": "DOCUMENT_MATERIALIZATION_LIFECYCLE",
            "has_local_overrides": False,
            "local_overrides": [],
        }


def test_instantiation_blocks_duplicate_host_node_id():
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        host = _host(work / "host.yaml")
        params = _params(work / "params.yaml", prefix="EXISTING")
        host_data = yaml.safe_load(host.read_text(encoding="utf-8"))
        host_data["nodes"].append({"id": "N_EXISTING_MATERIALIZE"})
        host.write_text(yaml.safe_dump(host_data), encoding="utf-8")
        report = instantiate_template(PACKAGE, "DOCUMENT_MATERIALIZATION_LIFECYCLE", params, work / "blocked.yaml", host)
        assert report["status"] == "failed"
        assert any(issue["code"] == "TM-NODE-ID-CONFLICT" for issue in report["issues"])


def test_factory_exposes_an_optional_confirmed_tree_module_route():
    program = yaml.safe_load((PACKAGE / "source" / "program.ordo.yaml").read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in program["nodes"]}

    recommendation = nodes["N_TREE_MODULE_TEMPLATE_RECOMMENDATION"]
    confirmation = nodes["N_TREE_MODULE_INSTANCE_CONFIRMATION"]
    terminal_binding = nodes["N_TERMINAL_OUTPUT_BINDING_POLICY"]

    assert recommendation["on_answer"]["use_document_lifecycle"]["next"] == "N_TREE_MODULE_INSTANCE_PARAMETER_REVIEW"
    assert confirmation["on_answer"]["confirm_materialization"]["next"] == "N_TERMINAL_OUTPUT_BINDING_POLICY"
    assert "N_TREE_MODULE_INSTANCE_CONFIRMATION" in terminal_binding["allowed_from"]
    assert program["state"]["schema"]["tree_module_instantiation_status"] == "not_started"
