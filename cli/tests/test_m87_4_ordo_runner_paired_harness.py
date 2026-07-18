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
from plain_prompt_runner import PlainPromptBaselineRunner, load_dataset, deterministic_pair_order
from ordo_runner import OrdoArmRunner, render_ordo_prompt
from paired_execution_harness import PairedExecutionHarness


class TestM874OrdoRunnerPairedHarness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = load_dataset(ROOT / "benchmarks/datasets/ordo_vs_plain_prompt_shared_tasks.v1.json")
        cls.schema = ROOT / "benchmarks/schemas/benchmark_run_evidence.schema.json"

    def _driver(self, root: Path, output):
        return BenchmarkDriver(
            adapter=FixtureAdapter(output),
            output_root=root / "runs",
            schema_path=self.schema,
            build_session_id="M87.4-TEST",
            current_tree_sha256="e" * 64,
        )

    def test_ordo_prompt_contains_ordo_controls(self):
        prompt = render_ordo_prompt(self.dataset["tasks"][0])
        self.assertIn("Ordo task", prompt)
        self.assertIn("state protection", prompt)
        self.assertIn("mandatory process gates", prompt)

    def test_ordo_runner_emits_arm_b_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            runner = OrdoArmRunner(self._driver(root, {"decision": "safe"}))
            result = runner.run_task(
                task=self.dataset["tasks"][0],
                model_id="fixture-model",
                repeat=1,
                pair_id="PAIR-X",
                run_id="RUN-B-001",
                seed=42,
            )
            self.assertEqual(result.arm, "B")
            metadata = json.loads((root / "runs/RUN-B-001/ab_metadata.json").read_text())
            self.assertEqual(metadata["arm"], "B")
            self.assertEqual(metadata["pair_id"], "PAIR-X")

    def test_harness_executes_both_arms(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            plain = PlainPromptBaselineRunner(self._driver(root, {"answer": "A"}))
            ordo = OrdoArmRunner(self._driver(root, {"answer": "B"}))
            harness = PairedExecutionHarness(
                plain_runner=plain,
                ordo_runner=ordo,
                output_root=root,
            )
            result = harness.run_pair(
                task=self.dataset["tasks"][0],
                model_id="fixture-model",
                repeat=1,
                seed=42,
            )
            self.assertTrue((root / "runs" / result.arm_a_run_id / "evidence.json").exists())
            self.assertTrue((root / "runs" / result.arm_b_run_id / "evidence.json").exists())

    def test_pair_manifest_binds_both_arms(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            harness = PairedExecutionHarness(
                plain_runner=PlainPromptBaselineRunner(self._driver(root, {"a": 1})),
                ordo_runner=OrdoArmRunner(self._driver(root, {"b": 1})),
                output_root=root,
            )
            result = harness.run_pair(
                task=self.dataset["tasks"][1],
                model_id="fixture-model",
                repeat=2,
            )
            manifest = json.loads(result.pair_manifest_path.read_text())
            self.assertEqual(set(manifest["arms"]), {"A", "B"})
            self.assertEqual(manifest["pair_id"], result.pair_id)

    def test_shared_payload_hash_matches_between_arms(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            harness = PairedExecutionHarness(
                plain_runner=PlainPromptBaselineRunner(self._driver(root, {"a": 1})),
                ordo_runner=OrdoArmRunner(self._driver(root, {"b": 1})),
                output_root=root,
            )
            result = harness.run_pair(
                task=self.dataset["tasks"][2],
                model_id="fixture-model",
                repeat=1,
            )
            a_meta = json.loads((root / "runs" / result.arm_a_run_id / "ab_metadata.json").read_text())
            b_meta = json.loads((root / "runs" / result.arm_b_run_id / "ab_metadata.json").read_text())
            self.assertEqual(a_meta["shared_payload_sha256"], b_meta["shared_payload_sha256"])

    def test_pair_order_is_respected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            harness = PairedExecutionHarness(
                plain_runner=PlainPromptBaselineRunner(self._driver(root, {"a": 1})),
                ordo_runner=OrdoArmRunner(self._driver(root, {"b": 1})),
                output_root=root,
            )
            result = harness.run_pair(
                task=self.dataset["tasks"][3],
                model_id="fixture-model",
                repeat=1,
            )
            self.assertEqual(result.order, deterministic_pair_order(result.pair_id))

    def test_existing_pair_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            harness = PairedExecutionHarness(
                plain_runner=PlainPromptBaselineRunner(self._driver(root, {"a": 1})),
                ordo_runner=OrdoArmRunner(self._driver(root, {"b": 1})),
                output_root=root,
            )
            kwargs = dict(
                task=self.dataset["tasks"][4],
                model_id="fixture-model",
                repeat=1,
            )
            harness.run_pair(**kwargs)
            with self.assertRaises(FileExistsError):
                harness.run_pair(**kwargs)


if __name__ == "__main__":
    unittest.main()
