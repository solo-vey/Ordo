from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from ordo.ci_release_evidence import source_tree_sha256, validate_ci_release_evidence
from ordo.package_profiles import build_package_profile


class TestM844NegativeReleaseGate(unittest.TestCase):
    def _payload(self, root: Path, *, status: str = "passed", matrix_status: str = "passed", issued_at: str | None = None):
        return {
            "schema_version": "ordo.ci_release_evidence.v1",
            "status": status,
            "revision": "abc",
            "run_id": "123",
            "issued_at": issued_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "source_tree_sha256": source_tree_sha256(root),
            "test_matrix": [{"id": "required-tests", "status": matrix_status}],
        }

    def _write_evidence(self, root: Path, payload: dict) -> Path:
        evidence = root / "ci_release_evidence.json"
        evidence.write_text(json.dumps(payload), encoding="utf-8")
        return evidence

    def test_stale_evidence_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "file.txt").write_text("x", encoding="utf-8")
            stale = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat().replace("+00:00", "Z")
            evidence = self._write_evidence(root, self._payload(root, issued_at=stale))
            codes = {item["code"] for item in validate_ci_release_evidence(root, evidence)}
            self.assertIn("ORDO-CI-010", codes)

    def test_red_ci_status_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "file.txt").write_text("x", encoding="utf-8")
            evidence = self._write_evidence(root, self._payload(root, status="failed"))
            codes = {item["code"] for item in validate_ci_release_evidence(root, evidence)}
            self.assertIn("ORDO-CI-003", codes)

    def test_red_matrix_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "file.txt").write_text("x", encoding="utf-8")
            evidence = self._write_evidence(root, self._payload(root, matrix_status="failed"))
            codes = {item["code"] for item in validate_ci_release_evidence(root, evidence)}
            self.assertIn("ORDO-CI-004", codes)

    def test_changed_tree_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "file.txt"
            target.write_text("x", encoding="utf-8")
            evidence = self._write_evidence(root, self._payload(root))
            target.write_text("changed", encoding="utf-8")
            codes = {item["code"] for item in validate_ci_release_evidence(root, evidence)}
            self.assertIn("ORDO-CI-005", codes)

    def test_missing_ci_evidence_cannot_be_bypassed_by_allow_unvalidated(self):
        import shutil
        source_package = Path(__file__).resolve().parents[2] / "packages" / "ordo_project_builder"
        with tempfile.TemporaryDirectory() as td:
            # M87.7: operate on an isolated copy — this negative-path call still
            # writes package_report.json, which must never land in the repo tree.
            package = Path(td) / "ordo_project_builder"
            shutil.copytree(source_package, package)
            out = Path(td) / "bypass.zip"
            report = build_package_profile(
                package,
                profile="dev",
                out=out,
                allow_unvalidated_output=True,
                ci_evidence=None,
            )
            self.assertEqual(report["status"], "failed")
            self.assertFalse(out.exists())
            self.assertIn("ORDO-CI-008", {item["code"] for item in report["issues"]})

    def test_invalid_revision_blocks_in_ci_environment(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "file.txt").write_text("x", encoding="utf-8")
            evidence = self._write_evidence(root, self._payload(root))
            with patch.dict(os.environ, {"GITHUB_SHA": "different"}, clear=False):
                codes = {item["code"] for item in validate_ci_release_evidence(root, evidence)}
            self.assertIn("ORDO-CI-006", codes)


if __name__ == "__main__":
    unittest.main()
