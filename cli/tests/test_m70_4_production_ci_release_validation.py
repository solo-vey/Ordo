from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


class M704ProductionCiReleaseValidationTests(unittest.TestCase):
    def test_production_policy_has_two_release_blocking_root_contracts(self) -> None:
        data = yaml.safe_load((REPO_ROOT / "repo_hygiene.yml").read_text(encoding="utf-8"))
        roots = {r["root_id"]: r for r in data["repo_hygiene"]["roots"]}
        for root_id in ("language_core", "cli_core"):
            self.assertEqual(roots[root_id]["clean_check"], "root_contract")
            self.assertTrue(roots[root_id]["release_blocking"])

    def test_ci_and_release_workflows_call_existing_repo_check(self) -> None:
        ci = (REPO_ROOT / ".github/workflows/ordo-clean-gate.yml").read_text(encoding="utf-8")
        release = (REPO_ROOT / ".github/workflows/ordo-release-clean-gate.yml").read_text(encoding="utf-8")
        self.assertIn("ordo repo-check .", ci)
        self.assertIn("--profile standard", ci)
        self.assertIn("--hygiene-scope development", ci)
        self.assertIn("--fail-on-warning", ci)
        self.assertIn("git archive --format=tar HEAD", release)
        self.assertIn("ordo repo-check .ordo-release-candidate", release)
        self.assertIn("--profile strict", release)
        self.assertIn("--hygiene-scope release", release)
        self.assertIn("--fail-on-warning", release)
        self.assertIn("release_clean_gate_provenance.json", release)

    def test_standard_and_strict_production_smokes_pass(self) -> None:
        for profile in ("standard", "strict"):
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / f"{profile}.json"
                cmd = [
                    sys.executable, "-m", "ordo.cli", "repo-check", ".", "--clean",
                    "--profile", profile, "--fail-on-warning", "--json", "--out", str(out),
                ]
                proc = subprocess.run(
                    cmd, cwd=REPO_ROOT, env={"PYTHONPATH": "cli", "PYTHONDONTWRITEBYTECODE": "1"},
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)
                report = json.loads(out.read_text(encoding="utf-8"))
                self.assertEqual(report["status"], "passed")
                hygiene = report["reports"]["repo_package_hygiene"]
                self.assertEqual(hygiene["status"], "passed")
                by_id = {r["root_id"]: r for r in hygiene["roots"]}
                self.assertEqual(by_id["language_core"]["status"], "passed")
                self.assertEqual(by_id["cli_core"]["status"], "passed")

    def test_workflow_yaml_is_parseable(self) -> None:
        for name in ("ordo-clean-gate.yml", "ordo-release-clean-gate.yml"):
            parsed = yaml.safe_load((REPO_ROOT / ".github/workflows" / name).read_text(encoding="utf-8"))
            self.assertIsInstance(parsed, dict)


if __name__ == "__main__":
    unittest.main()
