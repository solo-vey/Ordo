from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from ordo.canonical_source import validate_canonical_source
from ordo.evidence_identity import attach_evidence_identity, validate_evidence_report
from ordo.package_integrity import validate_package_integrity
from ordo.package_integrity import compare_reproducible_archives
from ordo.reporter import write_json


def package(tmp_path: Path, version: str = "1.2.3") -> Path:
    root = tmp_path / "pkg"
    (root / "source").mkdir(parents=True)
    (root / "source/program.ordo.yaml").write_text("nodes: []\n", encoding="utf-8")
    (root / "ordo.yml").write_text(f"name: demo\nversion: {version}\nsource: source/program.ordo.yaml\n", encoding="utf-8")
    return root


def test_evidence_identity_passes_and_stale_report_blocks(tmp_path: Path) -> None:
    root = package(tmp_path)
    report = attach_evidence_identity({"status": "passed"}, root, layers=["parse", "graph"], run_id="run-1")
    assert validate_evidence_report(report, root, required_layers=["parse", "graph"])["status"] == "passed"
    (root / "source/program.ordo.yaml").write_text("nodes: [changed]\n", encoding="utf-8")
    checked = validate_evidence_report(report, root, required_layers=["parse", "graph"])
    assert checked["status"] == "blocked"
    assert any(i["code"] == "EVIDENCE_SOURCE_MISMATCH" for i in checked["errors"])


def test_evidence_missing_layer_blocks(tmp_path: Path) -> None:
    root = package(tmp_path)
    report = attach_evidence_identity({}, root, layers=["parse"])
    checked = validate_evidence_report(report, root, required_layers=["parse", "graph"])
    assert checked["status"] == "blocked"
    assert any(i["code"] == "EVIDENCE_LAYER_MISSING" for i in checked["errors"])


def test_package_integrity_passes_and_version_drift_blocks(tmp_path: Path) -> None:
    root = package(tmp_path)
    (root / "output_templates").mkdir()
    (root / "output_templates" / "result.md").write_text("{{result}}\n", encoding="utf-8")
    passed = validate_package_integrity(root, expected_version="1.2.3")
    assert passed["status"] == "passed"
    assert passed["package_identity"]["component_inventory"]["templates"]
    assert validate_package_integrity(root, expected_version="9.9.9")["status"] == "blocked"


def test_package_integrity_detects_source_mutation(tmp_path: Path) -> None:
    root = package(tmp_path)
    checks = root / "SHA256SUMS.txt"
    source = root / "source/program.ordo.yaml"
    checks.write_text(f"{'0'*64}  source/program.ordo.yaml\n", encoding="utf-8")
    report = validate_package_integrity(root)
    assert report["status"] == "blocked"
    assert any(i["code"] == "PACKAGE_CHECKSUM_MISMATCH" for i in report["errors"])


def test_actual_current_report_is_bound_and_validated(tmp_path: Path) -> None:
    root = package(tmp_path)
    report_path = root / "reports" / "lint_report.json"
    write_json(report_path, {"status": "passed", "summary": {"errors": 0}})
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["evidence_identity"]["evidence_scope"] == "current_run"
    assert {item["layer"] for item in report["evidence_identity"]["validator_layers"]} >= {"parse", "schema", "graph"}
    assert validate_evidence_report(report, root, required_layers=["parse", "schema", "graph"])["status"] == "passed"


def test_evidence_cli_rejects_report_after_source_change(tmp_path: Path) -> None:
    root = package(tmp_path)
    report_path = root / "reports" / "artifact_validation_report.json"
    write_json(report_path, {"status": "passed"})
    (root / "source/program.ordo.yaml").write_text("nodes: [later]\n", encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "ordo.cli", "validate-evidence", str(root), str(report_path), "--required-layers", "artifact"], cwd=Path(__file__).parents[1], text=True, capture_output=True)
    assert result.returncode == 1
    assert "EVIDENCE_SOURCE_MISMATCH" in result.stdout


def test_package_integrity_rejects_mixed_version_current_evidence(tmp_path: Path) -> None:
    root = package(tmp_path)
    report = attach_evidence_identity({"status": "passed"}, root, layers=["parse"])
    report["evidence_identity"]["package_version"] = "wrong"
    (root / "reports").mkdir()
    (root / "reports" / "lint_report.json").write_text(json.dumps(report), encoding="utf-8")
    checked = validate_package_integrity(root)
    assert checked["status"] == "blocked"
    assert any(item["code"] == "PACKAGE_REPORT_VERSION_MISMATCH" for item in checked["errors"])


def test_reproducible_archive_comparison_is_payload_based(tmp_path: Path) -> None:
    import zipfile
    first, second = tmp_path / "one.zip", tmp_path / "two.zip"
    for archive in (first, second):
        with zipfile.ZipFile(archive, "w") as out:
            out.writestr("package/file.txt", "same")
    assert compare_reproducible_archives(first, second)["status"] == "passed"
    result = subprocess.run([sys.executable, "-m", "ordo.cli", "verify-reproducible-build", str(first), str(second)], cwd=Path(__file__).parents[1], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
