from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "clean_check"


class RepoCheckCleanIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_repo_check_clean_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def copy_fixture(self, fixture_name: str, target_name: str) -> Path:
        target = self.tmp / target_name
        shutil.copytree(FIXTURES / fixture_name, target)
        return target

    def write_policy(self, text: str) -> None:
        (self.tmp / "repo_hygiene.yml").write_text(text.strip() + "\n", encoding="utf-8")

    def run_repo_check(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "ordo.cli", "repo-check", str(self.tmp), "--clean", "--json", *extra],
            cwd=CLI_ROOT,
            text=True,
            capture_output=True,
        )

    def test_repo_check_clean_without_policy_is_not_applicable_and_does_not_wide_enforce_packages(self) -> None:
        packages = self.tmp / "packages"
        packages.mkdir()
        shutil.copytree(FIXTURES / "missing_source_yaml", packages / "delegated_applied_package")
        result = self.run_repo_check()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        report = json.loads(result.stdout)
        hygiene = report["reports"]["repo_package_hygiene"]
        self.assertEqual(hygiene["status"], "not_applicable")
        self.assertEqual(hygiene["summary"]["checked_count"], 0)
        self.assertEqual(hygiene["summary"]["delegated_count"], 1)
        self.assertNotIn("repo_package_hygiene", report["failed_checks"])

    def test_repo_check_clean_policy_required_clean_root_passes(self) -> None:
        self.copy_fixture("clean_minimal", "language_like_root")
        self.write_policy('''
repo_hygiene:
  default_profile: standard
  roots:
    - root_id: language_like_root
      path: language_like_root
      role: language_core
      clean_check: required
      release_blocking: true
''')
        result = self.run_repo_check()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        report = json.loads(result.stdout)
        hygiene = report["reports"]["repo_package_hygiene"]
        self.assertEqual(hygiene["status"], "passed")
        self.assertEqual(hygiene["summary"]["checked_count"], 1)
        self.assertEqual(hygiene["roots"][0]["status"], "passed")

    def test_repo_check_clean_policy_required_blocked_root_fails_repo_check(self) -> None:
        self.copy_fixture("missing_source_yaml", "broken_root")
        self.write_policy('''
repo_hygiene:
  default_profile: standard
  roots:
    - root_id: broken_root
      path: broken_root
      role: cli_utility
      clean_check: required
      release_blocking: true
''')
        result = self.run_repo_check()
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report["reports"]["repo_package_hygiene"]["status"], "blocked")
        self.assertIn("repo_package_hygiene", report["failed_checks"])

    def test_repo_check_clean_fail_on_warning_blocks_release_blocking_warning_root(self) -> None:
        self.copy_fixture("warning_fail_on_warning", "warning_root")
        self.write_policy('''
repo_hygiene:
  default_profile: light
  roots:
    - root_id: warning_root
      path: warning_root
      role: cli_utility
      clean_check: required
      release_blocking: true
''')
        result = self.run_repo_check("--profile", "light", "--fail-on-warning")
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        hygiene = report["reports"]["repo_package_hygiene"]
        self.assertEqual(hygiene["status"], "blocked")
        self.assertEqual(hygiene["roots"][0]["status"], "passed_with_warnings")


if __name__ == "__main__":
    unittest.main()
