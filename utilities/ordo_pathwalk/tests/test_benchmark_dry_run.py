import json
from pathlib import Path

from utilities.ordo_pathwalk.runner import dry_run


def test_benchmark_dry_run_orchestrates_two_scenarios_without_reusing_sandbox(tmp_path: Path, monkeypatch):
    def fake_prepare(tree_dir, sandbox_dir, runtime_view):
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        (sandbox_dir / "cli_embedded").mkdir(parents=True, exist_ok=True)
        (sandbox_dir / "cli_embedded" / "ordo").write_text("#!/bin/sh\n", encoding="utf-8")
        (sandbox_dir / "ordo.runtime.json").write_text(json.dumps({"runtime_view": runtime_view}), encoding="utf-8")

    def fake_case(*, tree_dir, scenario_path, runtime_view, out_dir, scenario_id=None):
        safe = runtime_view.replace(",", "_")
        scores = out_dir / "scores"
        scores.mkdir(parents=True, exist_ok=True)
        score_path = scores / f"{scenario_id}_{safe}_score.json"
        score_path.write_text(json.dumps({
            "gate_passed": True,
            "path_quality_score": 1.0,
            "cell_match_rate": 1.0,
            "protocol_compliance_rate": 1.0,
            "distraction_recovery_rate": 1.0,
            "backtrack_accuracy": 1.0,
            "runtime_view": runtime_view,
            "runtime_metadata": {"runtime_protocol_version": "M60.4", "runtime_view": runtime_view},
        }), encoding="utf-8")
        return {"status": "passed", "scenario_id": scenario_id, "runtime_view": runtime_view, "score_file": str(score_path)}

    monkeypatch.setattr(dry_run, "_prepare_m60_runtime_sandbox", fake_prepare)
    monkeypatch.setattr(dry_run, "run_dry_run_case", fake_case)

    summary = dry_run.run_benchmark_dry_run(
        tmp_path / "dry_run",
        scenario_count=2,
        depth=1,
        branching=(2, 2),
        runtime_views=("json",),
        force=True,
        worker_mode="in-process",
    )
    assert summary["benchmark_dry_run"]["status"] == "passed"
    assert summary["benchmark_dry_run"]["expected_cases"] == 2
    assert summary["benchmark_dry_run"]["passed_cases"] == 2
    assert (tmp_path / "dry_run" / "RAW_METRICS.csv").exists()
