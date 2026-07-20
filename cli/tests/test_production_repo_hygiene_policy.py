from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from ordo.repo_checks import run_repo_checks, run_repo_package_hygiene, run_repo_root_contract


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


    def test_root_contract_validates_required_and_parseable_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            target = root / "component"
            target.mkdir(parents=True)
            (target / "required.txt").write_text("required", encoding="utf-8")
            (target / "config.yaml").write_text("enabled: true\n", encoding="utf-8")
            (target / "data.json").write_text('{"ok": true}\n', encoding="utf-8")
            (target / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
            entry = {
                "path": "component",
                "contract": {
                    "required_paths": ["required.txt"],
                    "yaml_globs": ["*.yaml"],
                    "json_globs": ["*.json"],
                    "python_globs": ["*.py"],
                },
            }

            report = run_repo_root_contract(root, entry)

            self.assertEqual(report["status"], "passed")
            self.assertEqual(report["summary"]["blocked_count"], 0)
            self.assertEqual(report["summary"]["check_count"], 5)

    def test_root_contract_missing_required_path_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            (root / "component").mkdir(parents=True)
            entry = {
                "path": "component",
                "contract": {"required_paths": ["missing.txt"]},
            }

            report = run_repo_root_contract(root, entry)

            self.assertEqual(report["status"], "blocked")
            self.assertTrue(
                any(item["check_id"] == "root_contract_required_path" for item in report["errors"])
            )

    def test_root_contract_invalid_structured_files_are_blocking(self) -> None:
        cases = (
            ("yaml_globs", "broken.yaml", "[", "root_contract_yaml_parse"),
            ("json_globs", "broken.json", "{", "root_contract_json_parse"),
            ("python_globs", "broken.py", "def broken(", "root_contract_python_syntax"),
        )
        for glob_key, filename, content, check_id in cases:
            with self.subTest(check_id=check_id):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "repo"
                    target = root / "component"
                    target.mkdir(parents=True)
                    (target / filename).write_text(content, encoding="utf-8")
                    entry = {
                        "path": "component",
                        "contract": {glob_key: [filename]},
                    }

                    report = run_repo_root_contract(root, entry)

                    self.assertEqual(report["status"], "blocked")
                    self.assertTrue(any(item["check_id"] == check_id for item in report["errors"]))

    def test_root_contract_rejects_repository_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            entry = {"path": "../outside", "contract": {}}

            report = run_repo_root_contract(root, entry)

            self.assertEqual(report["status"], "blocked")
            self.assertEqual(report["errors"][0]["check_id"], "root_contract_path_within_repo")

    def test_root_contract_requires_mapping_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            (root / "component").mkdir(parents=True)
            entry = {"path": "component", "contract": ["not", "a", "mapping"]}

            report = run_repo_root_contract(root, entry)

            self.assertEqual(report["status"], "blocked")
            self.assertTrue(
                any(item["check_id"] == "root_contract_mapping" for item in report["errors"])
            )

    def test_malformed_repo_hygiene_policy_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "repo_hygiene.yml").write_text("repo_hygiene: [\n", encoding="utf-8")

            report = run_repo_package_hygiene(root, profile="standard")

            self.assertEqual(report["status"], "blocked")
            self.assertEqual(report["exit_code"], 1)
            self.assertTrue(
                any(item["check_id"] == "repo_hygiene_policy_parse" for item in report["errors"])
            )

    def test_optional_missing_root_is_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  roots:\n"
                "    - root_id: optional_component\n"
                "      path: optional_component\n"
                "      clean_check: optional\n",
                encoding="utf-8",
            )

            report = run_repo_package_hygiene(root, profile="standard")

            self.assertEqual(report["status"], "not_applicable")
            self.assertEqual(report["summary"]["not_applicable_count"], 1)
            self.assertEqual(report["summary"]["blocked_count"], 0)

    def test_unsupported_clean_check_is_delegated_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  roots:\n"
                "    - root_id: custom_component\n"
                "      path: custom_component\n"
                "      clean_check: custom\n",
                encoding="utf-8",
            )

            report = run_repo_package_hygiene(root, profile="standard")

            self.assertEqual(report["status"], "passed_with_warnings")
            self.assertEqual(report["summary"]["delegated_count"], 1)
            self.assertTrue(
                any(
                    item["check_id"] == "repo_hygiene_clean_check_treatment"
                    for item in report["warnings"]
                )
            )

if __name__ == "__main__":
    unittest.main()
