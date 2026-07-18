from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks"))
sys.path.insert(0, str(ROOT / "benchmarks/ab"))

from adapters import FixtureAdapter
from benchmark_driver import BenchmarkDriver
from plain_prompt_runner import (
    PlainPromptBaselineRunner,
    render_plain_prompt,
    deterministic_pair_order,
    load_dataset,
)


class TestM873PlainPromptBaselineRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset(ROOT / "benchmarks/datasets/ordo_vs_plain_prompt_shared_tasks.v1.json")
        cls.schema = ROOT / "benchmarks/schemas/benchmark_run_evidence.schema.json"

    def _driver(self, root: Path):
        return BenchmarkDriver(
            adapter=FixtureAdapter({"decision": "safe"}),
            output_root=root / "runs",
            schema_path=self.schema,
            build_session_id="M87.3-TEST",
            current_tree_sha256="d" * 64,
        )

    def test_rendered_plain_prompt_has_no_ordo_leakage(self):
        prompt = render_plain_prompt(self.dataset["tasks"][0])
        self.assertNotIn("Ordo", prompt)
        self.assertNotIn("STATE.SNAPSHOT", prompt)

    def test_rendered_prompt_contains_frozen_shared_content(self):
        task = self.dataset["tasks"][0]
        prompt = render_plain_prompt(task)
        self.assertIn(task["shared_input"]["scenario"], prompt)
        self.assertIn(task["acceptance_criteria"][0], prompt)
        self.assertIn(task["required_output"][0], prompt)

    def test_pair_order_is_deterministic(self):
        pair_id = "PAIR-AB-TASK-001-model-1"
        self.assertEqual(deterministic_pair_order(pair_id), deterministic_pair_order(pair_id))

    def test_runner_emits_arm_a_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runner = PlainPromptBaselineRunner(self._driver(root))
            result = runner.run_task(
                task=self.dataset["tasks"][0],
                model_id="fixture-model",
                repeat=1,
                run_id="RUN-A-001",
                seed=42,
            )
            self.assertEqual(result.arm, "A")
            metadata = json.loads((root / "runs/RUN-A-001/ab_metadata.json").read_text())
            self.assertEqual(metadata["arm"], "A")
            self.assertEqual(metadata["pair_id"], result.pair_id)

    def test_runner_emits_canonical_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runner = PlainPromptBaselineRunner(self._driver(root))
            result = runner.run_task(
                task=self.dataset["tasks"][1],
                model_id="fixture-model",
                repeat=1,
                run_id="RUN-A-002",
            )
            self.assertEqual(result.evidence["schema_version"], "ordo.benchmark_run_evidence.v1")
            self.assertEqual(result.evidence["benchmark_id"], "ordo-vs-plain-prompt-v1")

    def test_shared_payload_hash_is_recorded(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runner = PlainPromptBaselineRunner(self._driver(root))
            result = runner.run_task(
                task=self.dataset["tasks"][2],
                model_id="fixture-model",
                repeat=2,
                run_id="RUN-A-003",
            )
            metadata = json.loads((root / "runs/RUN-A-003/ab_metadata.json").read_text())
            self.assertEqual(metadata["shared_payload_sha256"], result.shared_payload_sha256)

    def test_existing_run_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runner = PlainPromptBaselineRunner(self._driver(root))
            kwargs = dict(
                task=self.dataset["tasks"][0],
                model_id="fixture-model",
                repeat=1,
                run_id="RUN-A-004",
            )
            runner.run_task(**kwargs)
            with self.assertRaises(FileExistsError):
                runner.run_task(**kwargs)


if __name__ == "__main__":
    unittest.main()
