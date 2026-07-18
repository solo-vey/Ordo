from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from ordo.repo_checks import run_repo_checks, validate_generated_metadata_absent


class M742HygieneScopeIsolationTests(unittest.TestCase):
    def test_development_scope_reports_local_transients_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache = root / "pkg" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "module.cpython-311.pyc").write_bytes(b"local bytecode")
            report = validate_generated_metadata_absent(root, scope="development")
            self.assertEqual(report["status"], "passed")
            self.assertEqual(report["forbidden_paths"], [])
            self.assertTrue(any("__pycache__" in p for p in report["observed_transient_paths"]))

    def test_release_scope_blocks_same_transients(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "cli" / "ordo.egg-info"
            metadata.mkdir(parents=True)
            (metadata / "PKG-INFO").write_text("Name: ordo\n", encoding="utf-8")
            report = validate_generated_metadata_absent(root, scope="release")
            self.assertEqual(report["status"], "failed")
            self.assertTrue(any("ordo.egg-info" in p for p in report["forbidden_paths"]))

    def test_development_scope_blocks_tracked_generated_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            cache = root / "pkg" / "__pycache__"
            cache.mkdir(parents=True)
            pyc = cache / "module.pyc"
            pyc.write_bytes(b"tracked bytecode")
            subprocess.run(["git", "-C", str(root), "add", "-f", "pkg/__pycache__/module.pyc"], check=True)
            report = validate_generated_metadata_absent(root, scope="development")
            self.assertEqual(report["status"], "failed")
            self.assertEqual(report["evidence_mode"], "git_tracked_files")
            self.assertIn("pkg/__pycache__/module.pyc", report["forbidden_paths"])

    def test_repo_check_exposes_selected_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "__pycache__").mkdir()
            development = run_repo_checks(root, hygiene_scope="development")
            release = run_repo_checks(root, hygiene_scope="release")
            self.assertEqual(development["status"], "passed")
            self.assertEqual(development["hygiene_scope"], "development")
            self.assertEqual(release["status"], "failed")
            self.assertEqual(release["hygiene_scope"], "release")


if __name__ == "__main__":
    unittest.main()
