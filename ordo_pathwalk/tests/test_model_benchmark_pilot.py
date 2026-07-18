from __future__ import annotations

import csv
import json
from pathlib import Path

from ordo_pathwalk.runner.model_benchmark import create_transcript_replay_pilot, collect_model_benchmark_results


def test_transcript_replay_pilot_writes_protocol_artifacts(tmp_path: Path) -> None:
    out = tmp_path / "pilot"
    summary = create_transcript_replay_pilot(
        out,
        scenario_count=3,
        depth=1,
        branching=(2, 2),
        runtime_views=("json",),
        force=True,
    )

    assert summary["status"] == "passed-pilot"
    assert summary["completed_cases"] == 3
    assert summary["calibration_eligible"] is False
    assert summary["weights_locked"] is True
    assert summary["failure_buckets"]["none"] == 1
    assert summary["failure_buckets"]["distraction_followed"] == 1
    assert summary["failure_buckets"]["protocol_violation"] == 1

    for name in [
        "MODEL_BENCHMARK_PLAN.json",
        "RAW_MODEL_METRICS.csv",
        "SUMMARY.json",
        "SUMMARY.md",
        "MODEL_RUN_MANIFEST.json",
        "CALIBRATION_DECISION.md",
        "CALIBRATION_DECISION.json",
    ]:
        assert (out / name).exists(), name

    rows = list(csv.DictReader((out / "RAW_MODEL_METRICS.csv").open(encoding="utf-8")))
    assert len(rows) == 3
    assert {row["runtime_view"] for row in rows} == {"json"}
    assert any(float(row["path_quality_score"]) < 1.0 for row in rows)
    assert all(row["transcript_sha256"].startswith("sha256:") for row in rows)

    plan = json.loads((out / "MODEL_BENCHMARK_PLAN.json").read_text(encoding="utf-8"))
    assert plan["benchmark_mode"] == "transcript-replay"
    assert plan["weights_locked"] is True
    assert len(plan["jobs"]) == 3

    collected = collect_model_benchmark_results(out / "MODEL_BENCHMARK_PLAN.json")
    assert collected["calibration_gates"]["nonzero_variance"]["passed"] is True
    assert collected["calibration_gates"]["sufficient_cases"]["passed"] is False
