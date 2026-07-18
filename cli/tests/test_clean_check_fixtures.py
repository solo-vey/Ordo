from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ordo.clean_check import run_clean_check

CLI_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "clean_check"


class CleanCheckFixtureSuiteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_clean_check_fixture_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fixture(self, name: str) -> Path:
        source = FIXTURES / name
        # A single test may need the same fixture under different profiles.
        # Copy to a unique temporary directory each time so CLI report output
        # never collides with an earlier run.
        target = Path(tempfile.mkdtemp(prefix=f"{name}_", dir=self.tmp))
        shutil.rmtree(target)
        shutil.copytree(source, target)
        return target

    def assert_status(self, fixture_name: str, expected: str, *, profile: str = "standard", fail_on_warning: bool = False) -> dict:
        report = run_clean_check(self.fixture(fixture_name), profile=profile, fail_on_warning=fail_on_warning)
        self.assertEqual(report["status"], expected, json.dumps(report, indent=2))
        return report

    def test_clean_minimal_passes(self) -> None:
        report = self.assert_status("clean_minimal", "passed")
        self.assertEqual(report["summary"]["error_count"], 0)
        self.assertEqual(report["summary"]["warning_count"], 0)

    def test_manifest_and_source_failures_block(self) -> None:
        for fixture_name in ("missing_manifest", "broken_manifest_yaml", "missing_source_yaml", "broken_source_yaml"):
            with self.subTest(fixture=fixture_name):
                report = self.assert_status(fixture_name, "blocked")
                self.assertGreater(report["summary"]["error_count"], 0)

    def test_prompt_manifest_checksum_mismatch_is_profile_sensitive(self) -> None:
        light = self.assert_status("prompt_manifest_checksum_mismatch", "passed_with_warnings", profile="light")
        self.assertEqual(light["summary"]["error_count"], 0)
        standard = self.assert_status("prompt_manifest_checksum_mismatch", "blocked", profile="standard")
        self.assertGreater(standard["summary"]["error_count"], 0)

    def test_prompt_refs_and_startup_entries_are_checked(self) -> None:
        self.assert_status("prompt_manifest_valid", "passed")
        self.assert_status("startup_entry_present", "passed")
        self.assert_status("prompt_ref_missing", "blocked")
        self.assert_status("startup_entry_missing", "blocked")

    def test_derived_artifacts_must_exist_or_be_backlogged(self) -> None:
        self.assert_status("derived_artifact_present", "passed")
        self.assert_status("derived_artifact_missing", "blocked")
        self.assert_status("derived_artifact_backlogged", "passed")

    def test_expired_delta_blocker_differs_between_standard_and_strict(self) -> None:
        standard = self.assert_status("expired_delta_blocker", "passed_with_warnings", profile="standard")
        self.assertEqual(standard["summary"]["error_count"], 0)
        strict = self.assert_status("expired_delta_blocker", "blocked", profile="strict")
        self.assertGreater(strict["summary"]["error_count"], 0)

    def test_fail_on_warning_changes_exit_code_without_changing_status(self) -> None:
        report = self.assert_status("warning_fail_on_warning", "passed_with_warnings", profile="light", fail_on_warning=True)
        self.assertEqual(report["exit_code"], 1)

    def test_cli_json_stdout_and_out_file_are_stable(self) -> None:
        package = self.fixture("clean_minimal")
        out = self.tmp / "clean_report.json"
        result = subprocess.run(
            [sys.executable, "-m", "ordo.cli", "clean-check", str(package), "--json", "--out", str(out)],
            cwd=CLI_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        stdout_report = json.loads(result.stdout)
        file_report = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(stdout_report["status"], "passed")
        self.assertEqual(file_report["mode"], "clean_package_check")
        self.assertEqual(stdout_report["summary"], file_report["summary"])


    def test_hardened_report_shape_is_stable(self) -> None:
        report = self.assert_status("clean_minimal", "passed")
        self.assertEqual(list(report.keys()), [
            "schema_version",
            "mode",
            "status",
            "profile_requested",
            "profile",
            "fail_on_warning",
            "exit_code",
            "package_root",
            "summary",
            "checks",
            "warnings",
            "errors",
            "exit_policy",
        ])
        self.assertEqual(report["schema_version"], "ordo.clean_check.report.v1")
        self.assertEqual(report["profile_requested"], "standard")
        self.assertEqual(report["profile"], "standard")
        self.assertEqual(report["exit_policy"], {"passed": 0, "passed_with_warnings": 0, "blocked": 1})
        for key in ("passed_count", "failed_count", "not_applicable_count"):
            self.assertIn(key, report["summary"])

    def test_invalid_programmatic_profile_is_reported_without_crashing(self) -> None:
        report = run_clean_check(self.fixture("clean_minimal"), profile="release")
        self.assertEqual(report["profile_requested"], "release")
        self.assertEqual(report["profile"], "standard")
        self.assertEqual(report["status"], "passed_with_warnings")
        self.assertEqual(report["summary"]["warning_count"], 1)
        self.assertEqual(report["warnings"][0]["check_id"], "profile_requested_valid")

    def test_cli_fail_on_warning_returns_nonzero(self) -> None:
        package = self.fixture("warning_fail_on_warning")
        result = subprocess.run(
            [sys.executable, "-m", "ordo.cli", "clean-check", str(package), "--profile", "light", "--fail-on-warning"],
            cwd=CLI_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("warnings:", result.stderr)


if __name__ == "__main__":
    unittest.main()
