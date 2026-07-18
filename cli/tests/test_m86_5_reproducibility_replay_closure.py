from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks"))

from adapters import FixtureAdapter
from benchmark_driver import BenchmarkDriver, BenchmarkRunConfig
from benchmark_replay import verify_run_directory, compare_replays, reproducibility_fingerprint
from benchmark_closure_gate import evaluate_closure_gate


class TestM865ReproducibilityReplayClosure(unittest.TestCase):
    def _driver(self, root: Path, model: str):
        return BenchmarkDriver(
            adapter=FixtureAdapter({"answer": 42}, resolved_model_id=model),
            output_root=root / "runs",
            schema_path=ROOT / "benchmarks/schemas/benchmark_run_evidence.schema.json",
            build_session_id="M86.5-TEST",
            current_tree_sha256="b" * 64,
        )

    def _config(self, run_id: str, model: str):
        return BenchmarkRunConfig(
            benchmark_id="csg-replay",
            dataset_version="M86.3-csg-adversarial-v2",
            protocol_version="M86.5",
            model=model,
            prompt="Evaluate",
            input_payload={"case": "CSG-ADV-001"},
            seed=42,
            run_id=run_id,
        )

    def test_replay_verifies_immutable_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._driver(root, "fixture-v1").run(self._config("RUN-1", "fixture"))
            report = verify_run_directory(
                root / "runs/RUN-1",
                ROOT / "benchmarks/schemas/benchmark_run_evidence.schema.json",
            )
            self.assertEqual(report["status"], "passed")

    def test_artifact_mutation_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._driver(root, "fixture-v1").run(self._config("RUN-2", "fixture"))
            (root / "runs/RUN-2/normalized_output.json").write_text('{"tampered":true}', encoding="utf-8")
            report = verify_run_directory(
                root / "runs/RUN-2",
                ROOT / "benchmarks/schemas/benchmark_run_evidence.schema.json",
            )
            self.assertIn("ORDO-REPLAY-006", {i["code"] for i in report["issues"]})

    def test_fingerprint_ignores_run_id_and_timestamps(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._driver(root, "fixture-v1").run(self._config("RUN-3", "fixture"))
            second = self._driver(root, "fixture-v1").run(self._config("RUN-4", "fixture"))
            self.assertEqual(reproducibility_fingerprint(first), reproducibility_fingerprint(second))

    def test_replay_comparison_passes_for_equivalent_runs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._driver(root, "fixture-v1").run(self._config("RUN-5", "fixture"))
            second = self._driver(root, "fixture-v1").run(self._config("RUN-6", "fixture"))
            self.assertEqual(compare_replays(first, second)["status"], "passed")

    def test_replay_comparison_detects_output_drift(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            first = self._driver(root, "fixture-v1").run(self._config("RUN-7", "fixture"))
            second = copy.deepcopy(first)
            second["artifacts"]["normalized_output_sha256"] = "0" * 64
            self.assertEqual(compare_replays(first, second)["status"], "failed")

    def test_closure_gate_passes_for_two_verified_models(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._driver(root, "fixture-v1").run(self._config("RUN-8", "fixture-a"))
            self._driver(root, "fixture-v2").run(self._config("RUN-9", "fixture-b"))
            gate = evaluate_closure_gate(
                [root / "runs/RUN-8", root / "runs/RUN-9"],
                ROOT / "benchmarks/schemas/benchmark_run_evidence.schema.json",
                minimum_runs=2,
                require_distinct_models=2,
            )
            self.assertEqual(gate["status"], "passed")

    def test_closure_gate_blocks_insufficient_model_diversity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._driver(root, "fixture-v1").run(self._config("RUN-10", "fixture-a"))
            gate = evaluate_closure_gate(
                [root / "runs/RUN-10"],
                ROOT / "benchmarks/schemas/benchmark_run_evidence.schema.json",
                minimum_runs=1,
                require_distinct_models=2,
            )
            self.assertIn("ORDO-CLOSURE-003", {i["code"] for i in gate["issues"]})


if __name__ == "__main__":
    unittest.main()
