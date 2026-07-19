from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "check_english_only_policy.py"
POLICY = ROOT / "policies" / "english_only_policy.yaml"

spec = importlib.util.spec_from_file_location("english_policy_validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

class EnglishOnlyPolicyF2Tests(unittest.TestCase):
    def validate_minimal(self, relative_path: str, content: str):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "tools").mkdir()
            (repo / "policies").mkdir()
            (repo / "tools/check_english_only_policy.py").write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
            (repo / "policies/english_only_policy.yaml").write_text(POLICY.read_text(encoding="utf-8"), encoding="utf-8")
            target = repo / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return validator.validate(repo, repo / "policies/english_only_policy.yaml")

    def test_unknown_markdown_blocks(self):
        self.assertEqual(self.validate_minimal("docs/x.md", "Український текст\n")["status"], "blocked")

    def test_unknown_yaml_blocks(self):
        report = self.validate_minimal("docs/x.yaml", "description: Український текст\n")
        self.assertEqual(report["status"], "blocked")
        self.assertGreater(report["violation_count"], 0)

    def test_unexpected_parse_failure_blocks(self):
        report = self.validate_minimal("docs/x.yaml", "broken: [Український текст\n")
        self.assertEqual(report["status"], "blocked")
        self.assertGreater(report["parse_failure_count"], 0)

    def test_localized_field_passes(self):
        self.assertEqual(
            self.validate_minimal("packages/x/test.yaml", "display_name_uk: Зміна статусу\n")["status"],
            "passed",
        )

if __name__ == "__main__":
    unittest.main()
