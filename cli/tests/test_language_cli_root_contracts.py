from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from ordo.repo_checks import run_repo_package_hygiene, run_repo_root_contract

REPO_ROOT = Path(__file__).resolve().parents[2]


class LanguageCliRootContractTests(unittest.TestCase):
    def test_production_policy_enforces_language_and_cli_contracts(self) -> None:
        data = yaml.safe_load((REPO_ROOT / "repo_hygiene.yml").read_text(encoding="utf-8"))
        roots = {item["root_id"]: item for item in data["repo_hygiene"]["roots"]}
        self.assertEqual(roots["language_core"]["clean_check"], "root_contract")
        self.assertTrue(roots["language_core"]["release_blocking"])
        self.assertEqual(roots["cli_core"]["clean_check"], "root_contract")
        self.assertTrue(roots["cli_core"]["release_blocking"])

    def test_production_root_contracts_pass(self) -> None:
        report = run_repo_package_hygiene(REPO_ROOT, profile="standard")
        by_id = {item["root_id"]: item for item in report["roots"]}
        self.assertEqual(report["status"], "passed")
        self.assertEqual(by_id["language_core"]["status"], "passed")
        self.assertEqual(by_id["cli_core"]["status"], "passed")
        self.assertGreater(by_id["language_core"]["summary"]["check_count"], 4)
        self.assertGreater(by_id["cli_core"]["summary"]["check_count"], 10)

    def test_missing_required_path_blocks_release_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "language").mkdir()
            entry = {"path": "language", "contract": {"required_paths": ["README.md"]}}
            report = run_repo_root_contract(root, entry)
            self.assertEqual(report["status"], "blocked")

    def test_invalid_python_blocks_cli_contract_without_bytecode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "cli" / "ordo").mkdir(parents=True)
            (root / "cli" / "ordo" / "bad.py").write_text("def broken(:\n", encoding="utf-8")
            entry = {"path": "cli", "contract": {"python_globs": ["ordo/*.py"]}}
            report = run_repo_root_contract(root, entry)
            self.assertEqual(report["status"], "blocked")
            self.assertFalse(any(root.rglob("__pycache__")))


if __name__ == "__main__":
    unittest.main()
