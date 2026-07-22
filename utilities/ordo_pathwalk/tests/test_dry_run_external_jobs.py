import json
from pathlib import Path

from utilities.ordo_pathwalk.runner import dry_run


def test_external_job_plan_job_collect_contract(tmp_path: Path, monkeypatch):
    def fake_prepare(tree_dir, sandbox_dir, runtime_view):
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        (sandbox_dir / "cli_embedded").mkdir(parents=True, exist_ok=True)
        (sandbox_dir / "cli_embedded" / "ordo").write_text("#!/bin/sh\n", encoding="utf-8")
        (sandbox_dir / "ordo.runtime.json").write_text(json.dumps({"runtime_view": runtime_view}), encoding="utf-8")

    def fake_case(*, tree_dir, scenario_path, runtime_view, out_dir, scenario_id=None):
        safe = runtime_view.replace(",", "_")
        for name in ("scores", "transcripts", "sandboxes"):
            (out_dir / name).mkdir(parents=True, exist_ok=True)
        score_path = out_dir / "scores" / f"{scenario_id}_{safe}_score.json"
        score_path.write_text(json.dumps({
            "gate_passed": True,
            "path_quality_score": 1.0,
            "cell_match_rate": 1.0,
            "protocol_compliance_rate": 1.0,
            "distraction_recovery_rate": 1.0,
            "backtrack_accuracy": 1.0,
            "turn_accuracy_rate": 1.0,
            "runtime_view": runtime_view,
            "runtime_metadata": {"runtime_protocol_version": "M60.4", "runtime_view": runtime_view},
        }), encoding="utf-8")
        return {"status": "passed", "scenario_id": scenario_id, "runtime_view": runtime_view, "score_file": str(score_path)}

    monkeypatch.setattr(dry_run, "_prepare_m60_runtime_sandbox", fake_prepare)
    monkeypatch.setattr(dry_run, "run_dry_run_case", fake_case)

    out_dir = tmp_path / "dry_run"
    plan = dry_run.create_dry_run_plan(
        out_dir,
        scenario_count=2,
        depth=1,
        branching=(2, 2),
        runtime_views=("json",),
        force=True,
    )
    assert plan["expected_cases"] == 2
    plan_path = out_dir / "DRY_RUN_PLAN.json"

    for job in plan["jobs"]:
        result = dry_run.run_dry_run_job(plan_path, job_id=job["job_id"])
        assert result["status"] == "passed"

    summary = dry_run.collect_dry_run_results(plan_path)
    assert summary["benchmark_dry_run"]["status"] == "passed"
    assert summary["benchmark_dry_run"]["execution_contract"] == "artifact-only-external-job"
    assert summary["benchmark_dry_run"]["passed_cases"] == 2
    assert (out_dir / "RAW_METRICS.csv").exists()
    assert (out_dir / "SUMMARY.json").exists()
