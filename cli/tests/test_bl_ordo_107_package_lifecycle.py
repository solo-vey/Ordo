from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from ordo.package_lifecycle import validate_package_lifecycle, validate_unpacked_release
from ordo.release import validate_release


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_package(tmp_path: Path) -> Path:
    root = tmp_path / "package"
    (root / "source").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "maintenance").mkdir()
    (root / "lifecycle").mkdir()
    source = root / "source/program.ordo.yaml"
    source.write_text("ordo:\n  version: '0.12'\n  package: demo.lifecycle\n  control_level: standard\n  execution_mode: full_runtime\nnodes: []\n", encoding="utf-8")
    digest = _sha(source)
    (root / "README.md").write_text("# Demo\n", encoding="utf-8")
    (root / "tests/test_cases.yaml").write_text("test_cases: []\n", encoding="utf-8")
    (root / "maintenance/apply_patch.py").write_text(f"LIFECYCLE_PATCH_IDEMPOTENT = True\nBASELINE_SOURCE_SHA256 = '{digest}'\n", encoding="utf-8")
    (root / "lifecycle/checkpoint.json").write_text(json.dumps({"immutable": True, "package_version": "1.1.0", "source_sha256": digest}), encoding="utf-8")
    previous = {"status": "passed", "package_version": "1.0.0", "source_identity": {"sha256": "0" * 64}}
    (root / "lifecycle/previous_release.json").write_text(json.dumps(previous), encoding="utf-8")
    current = {"schema_version": "ordo.canonical_regression_report.v1", "status": "passed", "source_identity": {"sha256": digest}}
    (root / "lifecycle/regression.json").write_text(json.dumps(current), encoding="utf-8")
    (root / "lifecycle/release_evidence.json").write_text(json.dumps(current), encoding="utf-8")
    manifest = f"""name: demo.lifecycle
version: '1.1.0'
source: source/program.ordo.yaml
tests: tests/test_cases.yaml
maintenance_lifecycle:
  version: '1.0'
  mode: strict
  required_assets: [README.md, tests/test_cases.yaml, maintenance/apply_patch.py]
  checkpoint: {{path: lifecycle/checkpoint.json}}
  patch: {{path: maintenance/apply_patch.py, baseline_source_sha256: {digest}, idempotent: true}}
  previous_release: {{path: lifecycle/previous_release.json}}
  regression: {{path: lifecycle/regression.json}}
  release_evidence: {{path: lifecycle/release_evidence.json}}
  runtime_excluded_paths: [maintenance]
"""
    (root / "ordo.yml").write_text(manifest, encoding="utf-8")
    return root


def test_lifecycle_binds_source_checkpoint_patch_version_and_evidence(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    report = validate_package_lifecycle(package, verify_baseline=True)
    assert report["status"] == "passed", report
    assert report["source_identity"]["sha256"]


def test_failed_patch_baseline_blocks_lifecycle(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    source = package / "source/program.ordo.yaml"
    source.write_text(source.read_text(encoding="utf-8") + "# changed\n", encoding="utf-8")
    report = validate_package_lifecycle(package, verify_baseline=True)
    assert report["status"] == "blocked"
    assert any(issue["code"] == "LIFECYCLE_PATCH_BASELINE_MISMATCH" for issue in report["issues"])


def test_independently_unpacked_release_revalidates_full_lifecycle(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    archive = tmp_path / "release.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        for path in package.rglob("*"):
            if path.is_file():
                bundle.write(path, Path("release") / path.relative_to(package))
    report = validate_unpacked_release(archive)
    assert report["status"] == "passed", report
    assert report["unpacked_archive"]["sha256"] == _sha(archive)


def test_release_gate_blocks_enabled_lifecycle_when_maintenance_asset_is_missing(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    (package / "maintenance/apply_patch.py").unlink()
    report = validate_release(package, skip_runtime=True)
    assert report["status"] == "failed"
    assert any(issue["code"] == "LIFECYCLE_VALIDATION_FAILED" for issue in report["issues"])
