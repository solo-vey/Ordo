from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "ordo-release-clean-gate.yml"
SCHEMA = ROOT / "language" / "schemas" / "release_clean_gate_provenance_schema.yaml"


class ReleaseCleanGateProvenanceLinkageContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_v2_provenance_schema_and_sha256_linkage(self) -> None:
        self.assertIn("ordo.release_clean_gate.provenance.v2", self.text)
        self.assertIn("sha256(report_bytes).hexdigest()", self.text)
        self.assertIn('"report_sha256": report_sha256', self.text)
        self.assertIn('"report_size_bytes": report_size_bytes', self.text)

    def test_mirrors_report_identity_without_recalculating_status(self) -> None:
        self.assertIn('report.get("schema_version")', self.text)
        self.assertIn('report.get("status")', self.text)
        self.assertIn('report.get("exit_code")', self.text)
        self.assertIn('report.get("profile")', self.text)
        self.assertNotIn("if report_status ==", self.text)

    def test_missing_report_is_explicit_and_upload_remains_strict(self) -> None:
        self.assertIn('linkage_status = "report_missing"', self.text)
        self.assertIn('linkage_status = "linked"', self.text)
        self.assertIn("if-no-files-found: error", self.text)

    def test_schema_exists_and_declares_linkage_contract(self) -> None:
        self.assertTrue(SCHEMA.is_file())
        text = SCHEMA.read_text(encoding="utf-8")
        self.assertIn("ordo.release_clean_gate.provenance.v2", text)
        self.assertIn("report_sha256", text)
        self.assertIn("report_size_bytes", text)
        self.assertIn("report_missing", text)

    def test_hash_invariant_example(self) -> None:
        payload = b'{"status":"passed"}\n'
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual(len(digest), 64)
        self.assertEqual(digest, hashlib.sha256(payload).hexdigest())


if __name__ == "__main__":
    unittest.main()
