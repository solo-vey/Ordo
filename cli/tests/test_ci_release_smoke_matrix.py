from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CLI_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "clean_check"


class CiReleaseSmokeMatrixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ordo_m69_4_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def copy_fixture(self, name: str, target: str) -> Path:
        path = self.tmp / target
        shutil.copytree(FIXTURES / name, path)
        return path

    def write_policy(self, root_id: str, path: str, *, profile: str = "standard", release_blocking: bool = True) -> None:
        self.tmp.joinpath("repo_hygiene.yml").write_text(
            "repo_hygiene:\n"
            f"  default_profile: {profile}\n"
            "  roots:\n"
            f"    - root_id: {root_id}\n"
            f"      path: {path}\n"
            "      role: language_core\n"
            "      clean_check: required\n"
            f"      release_blocking: {'true' if release_blocking else 'false'}\n",
            encoding="utf-8",
        )

    def run_gate(self, *, profile: str, fail_on_warning: bool, out_rel: str) -> subprocess.CompletedProcess[str]:
        out = self.tmp / out_rel
        cmd = [sys.executable, "-m", "ordo.cli", "repo-check", str(self.tmp), "--clean", "--profile", profile, "--json", "--out", str(out)]
        if fail_on_warning:
            cmd.append("--fail-on-warning")
        return subprocess.run(cmd, cwd=CLI_ROOT, text=True, capture_output=True)

    def test_matrix_clean_root_passes_pr_main_and_release(self) -> None:
        self.copy_fixture("clean_minimal", "root")
        self.write_policy("root", "root")
        for gate, profile, fail in (("pr", "standard", False), ("main", "standard", True), ("release", "strict", True)):
            with self.subTest(gate=gate):
                result = self.run_gate(profile=profile, fail_on_warning=fail, out_rel=f"reports/{gate}.json")
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                report = json.loads(result.stdout)
                self.assertEqual(report["reports"]["repo_package_hygiene"]["status"], "passed")
                self.assertTrue((self.tmp / f"reports/{gate}.json").is_file())

    def test_matrix_warning_passes_pr_but_blocks_main_and_release(self) -> None:
        self.copy_fixture("warning_fail_on_warning", "root")
        self.write_policy("root", "root", profile="light")
        pr = self.run_gate(profile="light", fail_on_warning=False, out_rel="reports/pr.json")
        main = self.run_gate(profile="light", fail_on_warning=True, out_rel="reports/main.json")
        release = self.run_gate(profile="light", fail_on_warning=True, out_rel="reports/release.json")
        self.assertEqual(pr.returncode, 0, pr.stderr + pr.stdout)
        self.assertEqual(main.returncode, 1)
        self.assertEqual(release.returncode, 1)

    def test_matrix_blocked_root_blocks_all_gate_classes(self) -> None:
        self.copy_fixture("missing_source_yaml", "root")
        self.write_policy("root", "root")
        for gate, profile, fail in (("pr", "standard", False), ("main", "standard", True), ("release", "strict", True)):
            with self.subTest(gate=gate):
                result = self.run_gate(profile=profile, fail_on_warning=fail, out_rel=f"reports/{gate}.json")
                self.assertEqual(result.returncode, 1)

    def test_matrix_without_policy_is_not_applicable_and_non_blocking(self) -> None:
        packages = self.tmp / "packages"
        packages.mkdir()
        shutil.copytree(FIXTURES / "missing_source_yaml", packages / "delegated")
        result = self.run_gate(profile="strict", fail_on_warning=True, out_rel="reports/no_policy.json")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        report = json.loads(result.stdout)
        hygiene = report["reports"]["repo_package_hygiene"]
        self.assertEqual(hygiene["status"], "not_applicable")
        self.assertEqual(hygiene["summary"]["delegated_count"], 1)

    def test_report_stdout_and_out_file_are_equivalent_json(self) -> None:
        self.copy_fixture("clean_minimal", "root")
        self.write_policy("root", "root")
        result = self.run_gate(profile="strict", fail_on_warning=True, out_rel="reports/release.json")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        stdout_report = json.loads(result.stdout)
        file_report = json.loads((self.tmp / "reports/release.json").read_text(encoding="utf-8"))
        self.assertEqual(stdout_report, file_report)

    def test_release_provenance_hash_linkage_smoke(self) -> None:
        self.copy_fixture("clean_minimal", "root")
        self.write_policy("root", "root")
        result = self.run_gate(profile="strict", fail_on_warning=True, out_rel="reports/release/repo_clean_check.json")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        report_path = self.tmp / "reports/release/repo_clean_check.json"
        report_bytes = report_path.read_bytes()
        report = json.loads(report_bytes.decode("utf-8"))
        provenance = {
            "schema_version": "ordo.release_clean_gate.provenance.v2",
            "profile": "strict",
            "fail_on_warning": True,
            "linkage": {
                "status": "linked",
                "report_path": "reports/release/repo_clean_check.json",
                "report_schema_version": report.get("schema_version"),
                "report_status": report.get("status"),
                "report_exit_code": report.get("exit_code"),
                "report_profile": report.get("profile"),
                "report_sha256": hashlib.sha256(report_bytes).hexdigest(),
                "report_size_bytes": len(report_bytes),
            },
        }
        self.assertEqual(provenance["linkage"]["report_sha256"], hashlib.sha256(report_bytes).hexdigest())
        self.assertEqual(provenance["linkage"]["report_size_bytes"], report_path.stat().st_size)
        self.assertEqual(provenance["linkage"]["report_status"], report["status"])


if __name__ == "__main__":
    unittest.main()
