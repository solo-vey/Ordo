from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from ordo.repo_checks import run_repo_checks, run_repo_package_hygiene


REPO_ROOT = Path(__file__).resolve().parents[2]


class ProductionRepoHygienePolicyTests(unittest.TestCase):
    def test_policy_declares_truthful_initial_treatments(self) -> None:
        policy_path = REPO_ROOT / "repo_hygiene.yml"
        data = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
        policy = data["repo_hygiene"]
        roots = {item["root_id"]: item for item in policy["roots"]}

        self.assertEqual(data["schema_version"], "ordo.repo_hygiene.policy.v2")
        self.assertEqual(policy["policy_status"], "unified_development_release_contract")
        self.assertEqual(roots["language_core"]["clean_check"], "root_contract")
        self.assertEqual(roots["cli_core"]["clean_check"], "root_contract")
        self.assertEqual(roots["applied_packages"]["clean_check"], "delegated")
        self.assertEqual(roots["canonical_cli_example"]["clean_check"], "optional")
        self.assertFalse(any(item["clean_check"] == "required" for item in roots.values()))
        self.assertTrue(roots["language_core"]["release_blocking"])
        self.assertTrue(roots["cli_core"]["release_blocking"])
        self.assertIn(".DS_Store", policy["forbidden_paths"]["file_names"])
        self.assertIn(".ordo-generated", policy["forbidden_paths"]["directory_names"])

    def test_production_policy_runs_without_false_enforcement(self) -> None:
        report = run_repo_package_hygiene(REPO_ROOT, profile="standard")
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["policy_path"], "repo_hygiene.yml")
        self.assertEqual(report["summary"]["checked_count"], 3)
        self.assertEqual(report["summary"]["delegated_count"], 1)
        self.assertEqual(report["summary"]["not_applicable_count"], 6)
        self.assertEqual({item["root_id"] for item in report["roots"]}, {"language_core", "cli_core", "canonical_cli_example"})
        self.assertTrue(all(item["status"] == "passed" for item in report["roots"]))
        self.assertEqual(report["delegated_roots"][0]["root_id"], "applied_packages")

    def test_repo_check_clean_includes_applicable_policy_report(self) -> None:
        report = run_repo_checks(REPO_ROOT, clean=True, clean_profile="standard")
        hygiene = report["reports"]["repo_package_hygiene"]
        self.assertEqual(report["status"], "passed")
        self.assertEqual(hygiene["status"], "passed")
        self.assertEqual(hygiene["policy_path"], "repo_hygiene.yml")
        self.assertIn("repository_forbidden_paths", report["reports"])
        self.assertIn("duplicate_repository_nesting", report["reports"])

    def test_delegated_packages_are_not_individually_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            example = root / "example"
            example.mkdir(parents=True)
            (example / "program.ordo.yaml").write_text("program: {id: example}\n", encoding="utf-8")
            (example / "ordo.yml").write_text(
                "package_id: example\nsource_yaml: program.ordo.yaml\n",
                encoding="utf-8",
            )
            broken = root / "packages" / "synthetic_broken_package"
            broken.mkdir(parents=True)
            (broken / "ordo.yml").write_text("source_yaml: missing.yaml\n", encoding="utf-8")
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  roots:\n"
                "    - root_id: example\n"
                "      path: example\n"
                "      clean_check: optional\n"
                "    - root_id: applied_packages\n"
                "      path: packages\n"
                "      clean_check: delegated\n",
                encoding="utf-8",
            )
            report = run_repo_package_hygiene(root, profile="standard")
            self.assertNotEqual(report["status"], "blocked")
            self.assertEqual(report["summary"]["checked_count"], 1)
            self.assertFalse(any(item.get("path", "").startswith("packages/") for item in report["roots"]))


if __name__ == "__main__":
    unittest.main()
