from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ordo.build_identity import current_tree_sha256, new_build_identity, bind_report, validate_report_binding


class TestM851BuildIdentity(unittest.TestCase):
    def test_tree_identity_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.txt").write_text("A", encoding="utf-8")
            self.assertEqual(current_tree_sha256(root), current_tree_sha256(root))

    def test_tree_change_changes_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "a.txt"
            target.write_text("A", encoding="utf-8")
            before = current_tree_sha256(root)
            target.write_text("B", encoding="utf-8")
            self.assertNotEqual(before, current_tree_sha256(root))

    def test_build_session_is_explicit_and_unique(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.txt").write_text("A", encoding="utf-8")
            first = new_build_identity(root)
            second = new_build_identity(root)
            self.assertNotEqual(first["build_session_id"], second["build_session_id"])
            self.assertEqual(first["current_tree_sha256"], second["current_tree_sha256"])

    def test_report_binding_passes_for_same_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.txt").write_text("A", encoding="utf-8")
            identity = new_build_identity(root, build_session_id="session-1")
            report = bind_report({"status": "passed"}, identity)
            self.assertEqual(validate_report_binding(report, identity), [])

    def test_report_binding_rejects_cross_session(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.txt").write_text("A", encoding="utf-8")
            one = new_build_identity(root, build_session_id="session-1")
            two = new_build_identity(root, build_session_id="session-2")
            report = bind_report({"status": "passed"}, one)
            codes = {item["code"] for item in validate_report_binding(report, two)}
            self.assertIn("ORDO-BUILD-001", codes)


if __name__ == "__main__":
    unittest.main()
