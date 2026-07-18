from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "benchmarks"))

from adapters import FixtureAdapter
from benchmark_driver import BenchmarkDriver, BenchmarkRunConfig


class TestM862ProviderNeutralDriver(unittest.TestCase):
    def _driver(self, root: Path, adapter):
        return BenchmarkDriver(
            adapter=adapter,
            output_root=root / "runs",
            schema_path=ROOT / "benchmarks/schemas/benchmark_run_evidence.schema.json",
            build_session_id="M86.2-TEST",
            current_tree_sha256="a" * 64,
        )

    def test_successful_fixture_run_emits_canonical_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            driver = self._driver(root, FixtureAdapter({"answer": 42}))
            evidence = driver.run(BenchmarkRunConfig(
                benchmark_id="b1",
                dataset_version="d1",
                protocol_version="p1",
                model="fixture-model",
                prompt="Solve",
                input_payload={"x": 1},
                run_id="RUN-1",
            ))
            self.assertEqual(evidence["result"]["status"], "passed")
            self.assertEqual(evidence["provider"]["name"], "fixture")
            self.assertTrue((root / "runs/RUN-1/evidence.json").exists())

    def test_retry_records_final_attempt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            adapter = FixtureAdapter({"ok": True}, fail_times=1)
            driver = self._driver(root, adapter)
            evidence = driver.run(BenchmarkRunConfig(
                benchmark_id="b1",
                dataset_version="d1",
                protocol_version="p1",
                model="m",
                prompt="p",
                input_payload={},
                max_attempts=2,
                run_id="RUN-2",
            ))
            self.assertEqual(evidence["invocation"]["attempt"], 2)
            self.assertEqual(adapter.calls, 2)

    def test_terminal_provider_error_is_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            adapter = FixtureAdapter({}, fail_times=3)
            driver = self._driver(root, adapter)
            evidence = driver.run(BenchmarkRunConfig(
                benchmark_id="b1",
                dataset_version="d1",
                protocol_version="p1",
                model="m",
                prompt="p",
                input_payload={},
                max_attempts=2,
                run_id="RUN-3",
            ))
            self.assertEqual(evidence["result"]["status"], "error")
            self.assertEqual(evidence["invocation"]["attempt"], 2)
            self.assertIsNotNone(evidence["result"]["error"])

    def test_hashes_match_written_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            driver = self._driver(root, FixtureAdapter({"z": 1}))
            evidence = driver.run(BenchmarkRunConfig(
                benchmark_id="b1",
                dataset_version="d1",
                protocol_version="p1",
                model="m",
                prompt="abc",
                input_payload={"k": "v"},
                run_id="RUN-4",
            ))
            import hashlib
            run = root / "runs/RUN-4"
            self.assertEqual(
                evidence["artifacts"]["prompt_sha256"],
                hashlib.sha256((run / "prompt.txt").read_bytes()).hexdigest(),
            )
            self.assertEqual(
                evidence["artifacts"]["raw_output_sha256"],
                hashlib.sha256((run / "raw_output.json").read_bytes()).hexdigest(),
            )

    def test_existing_run_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            driver = self._driver(root, FixtureAdapter({"ok": True}))
            cfg = BenchmarkRunConfig(
                benchmark_id="b1",
                dataset_version="d1",
                protocol_version="p1",
                model="m",
                prompt="p",
                input_payload={},
                run_id="RUN-5",
            )
            driver.run(cfg)
            with self.assertRaises(FileExistsError):
                driver.run(cfg)


if __name__ == "__main__":
    unittest.main()
