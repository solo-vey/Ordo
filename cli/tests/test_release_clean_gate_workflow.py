from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "ordo-release-clean-gate.yml"


class ReleaseCleanGateWorkflowContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_exists_and_has_release_triggers(self) -> None:
        self.assertTrue(WORKFLOW.is_file())
        self.assertIn("pull_request:", self.text)
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("tags:", self.text)
        self.assertIn("- 'v*'", self.text)

    def test_workflow_uses_strict_existing_cli_gate(self) -> None:
        self.assertEqual(self.text.count("ordo repo-check ."), 1)
        self.assertIn("--clean", self.text)
        self.assertIn("--profile strict", self.text)
        self.assertIn("--hygiene-scope release", self.text)
        self.assertIn("--fail-on-warning", self.text)
        self.assertNotIn("clean_check.py", self.text)

    def test_release_candidate_is_isolated_tracked_tree_export(self) -> None:
        self.assertIn("git archive --format=tar HEAD", self.text)
        self.assertIn(".ordo-release-candidate", self.text)

    def test_release_evidence_contract(self) -> None:
        self.assertIn("--out reports/release/repo_clean_check.json", self.text)
        self.assertIn("release_clean_gate_provenance.json", self.text)
        self.assertIn("actions/upload-artifact@v4", self.text)
        self.assertIn("retention-days: 90", self.text)
        self.assertIn("if-no-files-found: error", self.text)

    def test_release_workflow_does_not_package_or_mutate_source_tree(self) -> None:
        self.assertNotIn("ordo package", self.text)
        self.assertNotIn("ordo compile", self.text)
        self.assertNotIn("validate-release", self.text)
        self.assertNotIn("packages/", self.text)


if __name__ == "__main__":
    unittest.main()
