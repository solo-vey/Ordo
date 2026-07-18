from __future__ import annotations
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from ordo.ci_release_evidence import source_tree_sha256, validate_ci_release_evidence

class TestM843CiBoundPackaging(unittest.TestCase):
    def _payload(self, root: Path, status: str = "passed"):
        return {
            "schema_version": "ordo.ci_release_evidence.v1",
            "status": "passed",
            "revision": "abc",
            "run_id": "123",
            "issued_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "source_tree_sha256": source_tree_sha256(root),
            "test_matrix": [{"id": "tests", "status": status}],
        }

    def test_green_matching_evidence_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root/"file.txt").write_text("x", encoding="utf-8")
            evidence = root/"reports/ci_release_evidence.json"; evidence.parent.mkdir(parents=True, exist_ok=True); evidence.write_text(json.dumps(self._payload(root)), encoding="utf-8")
            self.assertEqual(validate_ci_release_evidence(root, evidence), [])

    def test_tree_change_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root/"file.txt").write_text("x", encoding="utf-8")
            evidence = root/"reports/ci_release_evidence.json"; evidence.parent.mkdir(parents=True, exist_ok=True); evidence.write_text(json.dumps(self._payload(root)), encoding="utf-8")
            (root/"file.txt").write_text("changed", encoding="utf-8")
            self.assertIn("ORDO-CI-005", {x["code"] for x in validate_ci_release_evidence(root, evidence)})

    def test_red_matrix_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); (root/"file.txt").write_text("x", encoding="utf-8")
            evidence = root/"reports/ci_release_evidence.json"; evidence.parent.mkdir(parents=True, exist_ok=True); evidence.write_text(json.dumps(self._payload(root, "failed")), encoding="utf-8")
            self.assertIn("ORDO-CI-004", {x["code"] for x in validate_ci_release_evidence(root, evidence)})

if __name__ == "__main__":
    unittest.main()
