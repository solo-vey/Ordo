from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "ordo-clean-gate.yml"


class CiCleanGateWorkflowContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_exists_and_has_expected_triggers(self) -> None:
        self.assertTrue(WORKFLOW.is_file())
        self.assertIn("pull_request:", self.text)
        self.assertIn("push:", self.text)
        self.assertIn("- main", self.text)
        self.assertIn("- master", self.text)

    def test_workflow_uses_existing_repo_check_clean_cli(self) -> None:
        self.assertEqual(self.text.count("ordo repo-check ."), 2)
        self.assertEqual(self.text.count("--clean"), 2)
        self.assertEqual(self.text.count("--profile standard"), 2)
        self.assertEqual(self.text.count("--hygiene-scope development"), 2)
        self.assertNotIn("clean_check.py", self.text)

    def test_warning_policy_is_fail_closed_for_pr_and_main(self) -> None:
        pull_request_block = self.text.split("Run pull-request clean gate", 1)[1].split(
            "Run main-branch clean gate", 1
        )[0]
        main_block = self.text.split("Run main-branch clean gate", 1)[1].split(
            "Upload clean-gate evidence", 1
        )[0]
        self.assertIn("--fail-on-warning", pull_request_block)
        self.assertIn("--fail-on-warning", main_block)

    def test_report_and_artifact_contract(self) -> None:
        self.assertIn("--out reports/ci/repo_clean_check.json", self.text)
        self.assertIn("set -euo pipefail", self.text)
        self.assertIn("actions/upload-artifact@v4", self.text)
        self.assertIn("if: always()", self.text)
        self.assertIn("reports/ci/repo_clean_check.stdout.json", self.text)


if __name__ == "__main__":
    unittest.main()
