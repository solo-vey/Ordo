import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class GoldenExamplesContractTests(unittest.TestCase):
    def test_manifest_and_documentation_are_linked(self):
        manifest = json.loads((ROOT / "examples/golden_examples.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], "ordo.golden_examples.v1")
        ids = [item["id"] for item in manifest["examples"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, ["package-validation", "process-rail-next-step", "history-event-output-gate"])
        quickstart = (ROOT / "docs/QUICKSTART.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for example_id in ids:
            self.assertIn(f"--example {example_id}", quickstart)
        self.assertIn("docs/QUICKSTART.md", readme)
        self.assertIn("python -m pip install -e ./cli", quickstart)

    def test_commands_are_repository_root_relative(self):
        manifest = json.loads((ROOT / "examples/golden_examples.json").read_text(encoding="utf-8"))
        for example in manifest["examples"]:
            self.assertTrue(example["package"].startswith("packages/"))
            for command in example["commands"]:
                self.assertEqual(command[0], "ordo")
                self.assertNotIn("../", " ".join(command))

if __name__ == "__main__":
    unittest.main()
