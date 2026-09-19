from __future__ import annotations

import json
from pathlib import Path

from ordo.validation_layers import validate_layers
from ordo.validator_propagation import validate_validator_propagation


def _source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "demo.layers", "control_level": "standard", "execution_mode": "full_runtime"},
        "state": {"schema": {}},
        "graph_contract": {"entry_node": "N_START"},
        "nodes": [
            {"id": "N_START", "allow_unmatched_input": True, "on_answer": {"next": "N_DONE"}},
            {"id": "N_DONE", "terminal": True, "allow_unmatched_input": True},
        ],
    }


def test_layer_report_separates_all_required_validation_concerns() -> None:
    report = validate_layers(_source(), {"test_cases": []})
    assert report["status"] == "passed", report
    assert report["layer_order"] == ["schema", "graph", "lineage", "artifact", "semantic"]
    assert set(report["layers"]) == set(report["layer_order"])


def test_graph_failure_is_attributed_to_the_graph_layer() -> None:
    value = _source()
    value["nodes"][0]["on_answer"]["next"] = "N_MISSING"
    report = validate_layers(value, {"test_cases": []})
    assert report["status"] == "failed"
    assert report["layers"]["graph"]["status"] == "failed"
    assert "graph" in report["summary"]["failed_layers"]
    assert report["layers"]["schema"]["status"] == "passed"


def test_validator_propagation_fails_when_a_packaged_copy_drifts(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    package = tmp_path / "package"
    canonical = repo / "cli" / "ordo" / "validator.py"
    packaged = package / "cli_embedded" / "ordo_pkg" / "ordo" / "validator.py"
    canonical.parent.mkdir(parents=True)
    packaged.parent.mkdir(parents=True)
    canonical.write_text("VALUE = 'canonical'\n", encoding="utf-8")
    packaged.write_text(canonical.read_text(encoding="utf-8"), encoding="utf-8")
    (package / "validator_propagation_contract.json").write_text(json.dumps({
        "schema_version": "1.0",
        "mappings": [{"canonical": "cli/ordo/validator.py", "packaged": "cli_embedded/ordo_pkg/ordo/validator.py"}],
    }), encoding="utf-8")

    assert validate_validator_propagation(package, repo_root=repo)["status"] == "passed"
    canonical.write_text("VALUE = 'changed locally'\n", encoding="utf-8")
    report = validate_validator_propagation(package, repo_root=repo)
    assert report["status"] == "failed"
    assert report["issues"][0]["code"] == "VALIDATOR_PROPAGATION_HASH_MISMATCH"
