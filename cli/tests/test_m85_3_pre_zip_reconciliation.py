from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from ordo.build_identity import new_build_identity, bind_report
from ordo.package_reconciliation import pre_zip_reconciliation


class TestM853PreZipReconciliation(unittest.TestCase):
    def _write_bound_report(self, root: Path, identity: dict, status: str = "passed") -> Path:
        path = root / "reports" / "release_validation_report.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = bind_report({"status": status}, identity)
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_green_reconciliation_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "source.txt"
            src.write_text("x", encoding="utf-8")
            identity = new_build_identity(root, build_session_id="b1")
            report = self._write_bound_report(root, identity)
            result = pre_zip_reconciliation(root, identity, [report])
            self.assertEqual(result["status"], "passed")

    def test_changed_tree_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "source.txt"
            src.write_text("x", encoding="utf-8")
            identity = new_build_identity(root, build_session_id="b1")
            report = self._write_bound_report(root, identity)
            src.write_text("changed", encoding="utf-8")
            result = pre_zip_reconciliation(root, identity, [report])
            self.assertIn("ORDO-RECON-010", {i["code"] for i in result["issues"]})

    def test_failed_validation_report_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "source.txt").write_text("x", encoding="utf-8")
            identity = new_build_identity(root, build_session_id="b1")
            report = self._write_bound_report(root, identity, status="failed")
            result = pre_zip_reconciliation(root, identity, [report])
            self.assertIn("ORDO-RECON-013", {i["code"] for i in result["issues"]})

    def test_checksum_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "source.txt"
            src.write_text("x", encoding="utf-8")
            identity = new_build_identity(root, build_session_id="b1")
            report = self._write_bound_report(root, identity)
            checks = root / "SHA256SUMS.txt"
            checks.write_text("0" * 64 + "  source.txt\n", encoding="utf-8")
            result = pre_zip_reconciliation(root, identity, [report], checksum_manifest=checks)
            self.assertIn("ORDO-RECON-004", {i["code"] for i in result["issues"]})

    def test_build_manifest_hash_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "source.txt"
            src.write_text("x", encoding="utf-8")
            identity = new_build_identity(root, build_session_id="b1")
            report = self._write_bound_report(root, identity)
            manifest = root / "BUILD_MANIFEST.json"
            manifest.write_text(json.dumps({"files": [{"path": "source.txt", "sha256": "0" * 64}]}), encoding="utf-8")
            result = pre_zip_reconciliation(root, identity, [report], build_manifest=manifest)
            self.assertIn("ORDO-RECON-009", {i["code"] for i in result["issues"]})


if __name__ == "__main__":
    unittest.main()
