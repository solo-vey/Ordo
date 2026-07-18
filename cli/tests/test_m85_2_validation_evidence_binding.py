from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ordo.build_identity import new_build_identity
from ordo.validation_evidence import write_bound_validation_report, read_and_validate_bound_report


class TestM852ValidationEvidenceBinding(unittest.TestCase):
    def test_bound_report_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "source.txt").write_text("x", encoding="utf-8")
            identity = new_build_identity(root, build_session_id="build-1")
            path = root / "reports" / "validation.json"
            write_bound_validation_report({"status": "passed"}, identity, path)
            report, issues = read_and_validate_bound_report(path, identity)
            self.assertEqual(issues, [])
            self.assertEqual(report["build_identity"]["build_session_id"], "build-1")

    def test_cross_session_report_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "source.txt").write_text("x", encoding="utf-8")
            old = new_build_identity(root, build_session_id="old")
            new = new_build_identity(root, build_session_id="new")
            path = root / "reports" / "validation.json"
            write_bound_validation_report({"status": "passed"}, old, path)
            _, issues = read_and_validate_bound_report(path, new)
            self.assertIn("ORDO-BUILD-001", {i["code"] for i in issues})

    def test_changed_tree_report_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "source.txt"
            target.write_text("x", encoding="utf-8")
            old = new_build_identity(root, build_session_id="same")
            path = root / "reports" / "validation.json"
            write_bound_validation_report({"status": "passed"}, old, path)
            target.write_text("changed", encoding="utf-8")
            new = new_build_identity(root, build_session_id="same")
            _, issues = read_and_validate_bound_report(path, new)
            self.assertIn("ORDO-BUILD-002", {i["code"] for i in issues})

    def test_missing_report_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "source.txt").write_text("x", encoding="utf-8")
            identity = new_build_identity(root, build_session_id="build-1")
            _, issues = read_and_validate_bound_report(root / "missing.json", identity)
            self.assertIn("ORDO-BUILD-003", {i["code"] for i in issues})

    def test_invalid_json_report_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "source.txt").write_text("x", encoding="utf-8")
            identity = new_build_identity(root, build_session_id="build-1")
            path = root / "bad.json"
            path.write_text("{", encoding="utf-8")
            _, issues = read_and_validate_bound_report(path, identity)
            self.assertIn("ORDO-BUILD-004", {i["code"] for i in issues})


if __name__ == "__main__":
    unittest.main()
