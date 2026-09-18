from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ordo.artifact_lifecycle import advance_artifact_lifecycle, validate_artifact_lifecycle
from ordo.output_generator import generate_output


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _package(tmp_path: Path) -> Path:
    root = tmp_path / "artifact-package"
    (root / "source").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "ordo.yml").write_text("name: demo.artifact\nversion: '1.0.0'\nsource: source/program.ordo.yaml\ntests: tests/test_cases.yaml\n", encoding="utf-8")
    (root / "source/program.ordo.yaml").write_text("ordo:\n  version: '0.12'\n  package: demo.artifact\n  control_level: standard\n  execution_mode: full_runtime\nnodes: []\n", encoding="utf-8")
    (root / "tests/test_cases.yaml").write_text("test_cases: []\n", encoding="utf-8")
    return root


def _manifest(root: Path) -> tuple[Path, Path]:
    generated = root / "generated_outputs"
    generated.mkdir()
    artifact = generated / "artifact.md"
    artifact.write_text("# Artifact\n", encoding="utf-8")
    digest = _sha(artifact)
    data = {
        "schema": "ordo.output_manifest.v0.1",
        "artifacts": [
            {
                "id": "A_DEMO",
                "path": "generated_outputs/artifact.md",
                "hash": digest,
                "lifecycle": {
                    "state": "generated",
                    "generated": {"status": "generated", "path": "generated_outputs/artifact.md", "sha256": digest, "bytes": artifact.stat().st_size},
                    "reviewed": {"status": "not_reviewed"},
                    "approved": {"status": "not_approved"},
                    "delivery": {"status": "not_delivered", "download": {"href": "generated_outputs/artifact.md", "label": "Download artifact.md"}},
                },
            }
        ],
    }
    manifest = generated / "output_manifest.json"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    return manifest, artifact


def test_generator_materializes_physical_lifecycle_and_download_link(tmp_path: Path) -> None:
    package = _package(tmp_path)
    generated = generate_output(package)
    assert generated["status"] == "passed", generated
    manifest = json.loads((package / "generated_outputs/output_manifest.json").read_text(encoding="utf-8"))
    lifecycle = manifest["artifacts"][0]["lifecycle"]
    assert lifecycle["state"] == "generated"
    assert lifecycle["delivery"]["download"]["href"] == manifest["artifacts"][0]["path"]
    assert validate_artifact_lifecycle(package)["status"] == "passed"


def test_lifecycle_requires_review_before_approval_and_keeps_distinct_states(tmp_path: Path) -> None:
    package = _package(tmp_path)
    _manifest(package)
    premature = advance_artifact_lifecycle(package, artifact_id="A_DEMO", target_state="approved", actor="approver")
    assert premature["status"] == "blocked"
    assert any(issue["code"] == "ARTIFACT_LIFECYCLE_PREMATURE_TRANSITION" for issue in premature["issues"])
    assert advance_artifact_lifecycle(package, artifact_id="A_DEMO", target_state="reviewed", actor="reviewer")["status"] == "advanced"
    assert advance_artifact_lifecycle(package, artifact_id="A_DEMO", target_state="approved", actor="approver")["status"] == "advanced"
    assert advance_artifact_lifecycle(package, artifact_id="A_DEMO", target_state="delivered", actor="delivery-service")["status"] == "advanced"
    report = validate_artifact_lifecycle(package)
    assert report["status"] == "passed", report
    assert report["summary"]["states"] == {"generated": 0, "reviewed": 0, "approved": 0, "delivered": 1}


def test_missing_file_and_bad_download_link_block_completion_evidence(tmp_path: Path) -> None:
    package = _package(tmp_path)
    manifest, artifact = _manifest(package)
    artifact.unlink()
    report = validate_artifact_lifecycle(package)
    assert report["status"] == "blocked"
    assert any(issue["code"] == "ARTIFACT_PHYSICAL_FILE_MISSING" for issue in report["issues"])
    artifact.write_text("# Artifact\n", encoding="utf-8")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    data["artifacts"][0]["hash"] = _sha(artifact)
    data["artifacts"][0]["lifecycle"]["generated"]["sha256"] = _sha(artifact)
    data["artifacts"][0]["lifecycle"]["delivery"]["download"]["href"] = "generated_outputs/not-the-artifact.md"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    report = validate_artifact_lifecycle(package)
    assert report["status"] == "blocked"
    assert any(issue["code"] == "ARTIFACT_DOWNLOAD_LINK_INVALID" for issue in report["issues"])
