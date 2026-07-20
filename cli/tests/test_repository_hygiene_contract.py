from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from ordo.repo_checks import (
    validate_duplicate_repository_nesting,
    validate_package_generated_artifacts_absent,
    validate_repository_forbidden_paths,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class RepositoryHygieneContractTests(unittest.TestCase):
    def test_gitignore_contains_mandatory_categories(self) -> None:
        text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        for required in (
            "__pycache__/",
            "*.egg-info/",
            ".pytest_cache/",
            ".venv/",
            ".DS_Store",
            "._*",
            "__MACOSX/",
            ".ordo-generated/",
            ".ordo-release-candidate/",
            "reports/ci/",
            "reports/release/",
        ):
            self.assertIn(required, text)

    def test_development_scope_reports_untracked_pollution_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  forbidden_paths:\n"
                "    directory_names: [.venv]\n",
                encoding="utf-8",
            )
            (root / ".venv").mkdir()
            report = validate_repository_forbidden_paths(root, scope="development")
            self.assertEqual(report["status"], "passed")
            self.assertEqual(report["forbidden_paths"], [])
            self.assertIn(".venv", report["observed_transient_paths"])

    def test_development_scope_blocks_tracked_pollution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  forbidden_paths:\n"
                "    file_names: [.DS_Store]\n",
                encoding="utf-8",
            )
            (root / ".DS_Store").write_text("tracked", encoding="utf-8")
            subprocess.run(["git", "add", "-f", ".DS_Store"], cwd=root, check=True, capture_output=True)
            report = validate_repository_forbidden_paths(root, scope="development")
            self.assertEqual(report["status"], "failed")
            self.assertEqual(report["forbidden_paths"], [".DS_Store"])

    def test_release_scope_blocks_untracked_pollution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "candidate"
            root.mkdir()
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  forbidden_paths:\n"
                "    directory_names: [.pytest_cache]\n",
                encoding="utf-8",
            )
            (root / ".pytest_cache").mkdir()
            report = validate_repository_forbidden_paths(root, scope="release")
            self.assertEqual(report["status"], "failed")
            self.assertEqual(report["forbidden_paths"], [".pytest_cache"])

    def test_duplicate_nesting_blocks_adjacent_repetition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            nested = root / "bundle" / "bundle"
            nested.mkdir(parents=True)
            (nested / "file.txt").write_text("x", encoding="utf-8")
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  duplicate_nesting:\n"
                "    enabled: true\n"
                "    adjacent_segment_repetition: true\n",
                encoding="utf-8",
            )
            report = validate_duplicate_repository_nesting(root, scope="release")
            self.assertEqual(report["status"], "failed")
            self.assertIn("bundle/bundle", report["forbidden_paths"])

    def test_internal_ordo_package_name_is_not_repository_nesting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Ordo"
            package = root / "cli" / "ordo"
            package.mkdir(parents=True)
            (package / "__init__.py").write_text("", encoding="utf-8")
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  duplicate_nesting:\n"
                "    enabled: true\n"
                "    adjacent_segment_repetition: true\n"
                "    repository_name_repetition: true\n",
                encoding="utf-8",
            )
            report = validate_duplicate_repository_nesting(root, scope="release")
            self.assertEqual(report["status"], "passed")

    def test_top_level_repository_copy_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Ordo"
            nested = root / "Ordo" / "docs"
            nested.mkdir(parents=True)
            (nested / "README.md").write_text("duplicate", encoding="utf-8")
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  duplicate_nesting:\n"
                "    enabled: true\n"
                "    adjacent_segment_repetition: true\n"
                "    repository_name_repetition: true\n",
                encoding="utf-8",
            )
            report = validate_duplicate_repository_nesting(root, scope="release")
            self.assertEqual(report["status"], "failed")
            self.assertIn("Ordo", report["forbidden_paths"])

    def test_development_duplicate_nesting_ignores_untracked_local_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            nested = root / "local" / "local"
            nested.mkdir(parents=True)
            (nested / "file.txt").write_text("untracked", encoding="utf-8")
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  duplicate_nesting:\n"
                "    enabled: true\n"
                "    adjacent_segment_repetition: true\n",
                encoding="utf-8",
            )
            report = validate_duplicate_repository_nesting(root, scope="development")
            self.assertEqual(report["status"], "passed")
            self.assertEqual(report["forbidden_paths"], [])
            self.assertIn("local/local", report["observed_transient_paths"])

    def test_development_duplicate_nesting_blocks_tracked_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            nested = root / "tracked" / "tracked"
            nested.mkdir(parents=True)
            (nested / "file.txt").write_text("tracked", encoding="utf-8")
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  duplicate_nesting:\n"
                "    enabled: true\n"
                "    adjacent_segment_repetition: true\n",
                encoding="utf-8",
            )
            subprocess.run(
                ["git", "add", "tracked/tracked/file.txt", "repo_hygiene.yml"],
                cwd=root,
                check=True,
                capture_output=True,
            )
            report = validate_duplicate_repository_nesting(root, scope="development")
            self.assertEqual(report["status"], "failed")
            self.assertIn("tracked/tracked", report["forbidden_paths"])

    def test_repository_copy_finding_reports_duplicate_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "Ordo"
            nested = root / "Ordo" / "deep" / "docs"
            nested.mkdir(parents=True)
            (nested / "README.md").write_text("duplicate", encoding="utf-8")
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  duplicate_nesting:\n"
                "    enabled: true\n"
                "    repository_name_repetition: true\n",
                encoding="utf-8",
            )
            report = validate_duplicate_repository_nesting(root, scope="release")
            self.assertEqual(report["forbidden_paths"], ["Ordo"])

    def test_historical_transfer_prefix_is_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            nested = root / "TRANSFER_2026-07-14" / "bundle" / "bundle"
            nested.mkdir(parents=True)
            (nested / "file.txt").write_text("x", encoding="utf-8")
            (root / "repo_hygiene.yml").write_text(
                "repo_hygiene:\n"
                "  duplicate_nesting:\n"
                "    enabled: true\n"
                "    adjacent_segment_repetition: true\n"
                "    exempt_prefixes: [TRANSFER_2026-07-14/]\n",
                encoding="utf-8",
            )
            report = validate_duplicate_repository_nesting(root, scope="release")
            self.assertEqual(report["status"], "passed")


    def test_development_package_generated_untracked_is_reported_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            generated = root / "packages" / "demo" / "compiled" / "result.json"
            generated.parent.mkdir(parents=True)
            generated.write_text("{}", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)

            report = validate_package_generated_artifacts_absent(root, scope="development")

            self.assertEqual(report["status"], "passed")
            self.assertEqual(report["forbidden_paths"], [])
            self.assertEqual(report["observed_transient_paths"], ["packages/demo/compiled/result.json"])

    def test_development_package_generated_tracked_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            generated = root / "packages" / "demo" / "runtime" / "state.json"
            generated.parent.mkdir(parents=True)
            generated.write_text("{}", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "add", "packages/demo/runtime/state.json"], cwd=root, check=True, capture_output=True)

            report = validate_package_generated_artifacts_absent(root, scope="development")

            self.assertEqual(report["status"], "failed")
            self.assertEqual(report["forbidden_paths"], ["packages/demo/runtime/state.json"])

    def test_release_package_generated_untracked_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "candidate"
            generated = root / "packages" / "demo" / "generated_outputs" / "answer.txt"
            generated.parent.mkdir(parents=True)
            generated.write_text("generated", encoding="utf-8")

            report = validate_package_generated_artifacts_absent(root, scope="release")

            self.assertEqual(report["status"], "failed")
            self.assertEqual(report["forbidden_paths"], ["packages/demo/generated_outputs/answer.txt"])

    def test_package_generated_allowed_templates_remain_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "candidate"
            reports = root / "packages" / "demo" / "reports"
            compiled = root / "packages" / "demo" / "compiled"
            reports.mkdir(parents=True)
            compiled.mkdir(parents=True)
            (reports / "CLI_VALIDATION_SUMMARY.md").write_text("template", encoding="utf-8")
            (reports / "PACKAGE_PROFILE_SUMMARY.md").write_text("template", encoding="utf-8")
            (compiled / ".gitkeep").write_text("", encoding="utf-8")

            report = validate_package_generated_artifacts_absent(root, scope="release")

            self.assertEqual(report["status"], "passed")
            self.assertEqual(report["forbidden_paths"], [])
            self.assertEqual(report["observed_transient_paths"], [])


if __name__ == "__main__":
    unittest.main()
