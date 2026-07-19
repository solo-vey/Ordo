from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/ordo-delivery-gate.yml"
CHECK_WORKFLOW = ROOT / ".github/workflows/ordo-check.yml"
BUILDER = ROOT / "tools/build_release_archive.py"


class BlOrdo026DeliveryWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")
        cls.parsed = yaml.safe_load(cls.text)

    def test_workflow_is_parseable_and_has_manual_branch_tag_triggers(self) -> None:
        self.assertIsInstance(self.parsed, dict)
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("pull_request:", self.text)
        self.assertIn("- main", self.text)
        self.assertIn("- master", self.text)
        self.assertIn("- 'v*'", self.text)

    def test_full_gate_is_bounded_and_non_cancelling(self) -> None:
        self.assertIn("timeout-minutes: 90", self.text)
        self.assertIn("cancel-in-progress: false", self.text)
        self.assertIn("--test-timeout-seconds 3600", self.text)
        self.assertIn("--lint-timeout-seconds 900", self.text)

    def test_all_four_canonical_packages_are_linted(self) -> None:
        for package in (
            "history_event_guided_intake",
            "ordo_applied_project_factory",
            "ordo_hybrid_executor",
            "ordo_project_builder",
        ):
            self.assertIn(f"packages/{package}", self.text)

    def test_release_candidate_and_evidence_are_sha_bound(self) -> None:
        self.assertIn("dist/ORDO_ARF_CANONICAL_ORDO_2026_07_17_RC10.zip", self.text)
        self.assertIn("sha256sum dist/ORDO_ARF_CANONICAL_ORDO_2026_07_17_RC10.zip", self.text)
        self.assertIn("ordo.independent_delivery_ci_evidence.v1", self.text)
        self.assertIn("archive_sha256", self.text)
        self.assertIn("GITHUB_SHA", self.text)
        self.assertIn("GITHUB_RUN_ID", self.text)
        self.assertIn("if-no-files-found: error", self.text)
        self.assertIn(
            "cp DELIVERY_GATE_REPORT.json reports/ci/DELIVERY_GATE_REPORT.json",
            self.text,
        )
        self.assertIn(
            "cp FINAL_PACKAGE_SELF_CHECK_REPORT.json reports/ci/FINAL_PACKAGE_SELF_CHECK_REPORT.json",
            self.text,
        )

    def test_release_builder_materializes_fresh_self_check_for_ci_copy(self) -> None:
        builder = BUILDER.read_text(encoding="utf-8")
        self.assertIn(
            '(ROOT / "FINAL_PACKAGE_SELF_CHECK_REPORT.json").write_text(',
            builder,
        )
        self.assertIn("json.dumps(self_check, indent=2)", builder)

    def test_existing_check_workflow_includes_apf(self) -> None:
        check = CHECK_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("packages/ordo_applied_project_factory", check)


    def test_migration_aware_english_only_policy_is_integrated(self) -> None:
        command = "python tools/check_english_only_policy.py"
        self.assertIn(command, self.text)
        self.assertIn(command, CHECK_WORKFLOW.read_text(encoding="utf-8"))
        self.assertFalse((ROOT / ".github/workflows/english-only-policy.yml").exists())


if __name__ == "__main__":
    unittest.main()
