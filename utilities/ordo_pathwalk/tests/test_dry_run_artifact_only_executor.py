import json
from pathlib import Path

from utilities.ordo_pathwalk.runner import dry_run


def test_dry_run_plan_materializes_artifact_only_job_descriptors_and_scripts(tmp_path: Path, monkeypatch):
    def fake_prepare(tree_dir, sandbox_dir, runtime_view):
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        (sandbox_dir / "cli_embedded").mkdir(parents=True, exist_ok=True)
        (sandbox_dir / "cli_embedded" / "ordo").write_text("#!/bin/sh\n", encoding="utf-8")
        (sandbox_dir / "ordo.runtime.json").write_text(json.dumps({"runtime_view": runtime_view}), encoding="utf-8")

    monkeypatch.setattr(dry_run, "_prepare_m60_runtime_sandbox", fake_prepare)

    out_dir = tmp_path / "dry_run"
    plan = dry_run.create_dry_run_plan(
        out_dir,
        scenario_count=2,
        depth=1,
        branching=(2, 2),
        runtime_views=("json", "ordo-code"),
        force=True,
    )

    assert plan["mode"] == "artifact-only-external-job"
    assert plan["expected_cases"] == 4
    assert (out_dir / "DRY_RUN_PLAN.json").exists()
    assert (out_dir / "JOB_EXECUTION.md").exists()

    for job in plan["jobs"]:
        job_file = out_dir / "jobs" / f"{job['job_id']}.json"
        script_file = out_dir / "job_scripts" / f"{job['job_id']}.sh"
        assert job_file.exists()
        assert script_file.exists()
        descriptor = json.loads(job_file.read_text(encoding="utf-8"))
        assert descriptor["schema_version"] == "ordo.pathwalk.dry_run_job.v1"
        assert descriptor["execution_contract"] == "artifact-only-one-job"
        text = script_file.read_text(encoding="utf-8")
        assert "dry-run-job" in text
        assert "< /dev/null" in text


def test_collect_reports_artifact_only_execution_contract(tmp_path: Path, monkeypatch):
    def fake_prepare(tree_dir, sandbox_dir, runtime_view):
        sandbox_dir.mkdir(parents=True, exist_ok=True)
        (sandbox_dir / "cli_embedded").mkdir(parents=True, exist_ok=True)
        (sandbox_dir / "cli_embedded" / "ordo").write_text("#!/bin/sh\n", encoding="utf-8")
        (sandbox_dir / "ordo.runtime.json").write_text(json.dumps({"runtime_view": runtime_view}), encoding="utf-8")

    def fake_case(*, tree_dir, scenario_path, runtime_view, out_dir, scenario_id=None):
        safe = runtime_view.replace(",", "_")
        (out_dir / "scores").mkdir(parents=True, exist_ok=True)
        (out_dir / "transcripts").mkdir(parents=True, exist_ok=True)
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
        scenario_count=1,
        depth=1,
        branching=(2, 2),
        runtime_views=("json",),
        force=True,
    )
    result = dry_run.run_dry_run_job(out_dir / "DRY_RUN_PLAN.json", job_id=plan["jobs"][0]["job_id"])
    assert result["status"] == "passed"
    summary = dry_run.collect_dry_run_results(out_dir / "DRY_RUN_PLAN.json")
    assert summary["benchmark_dry_run"]["status"] == "passed"
    assert summary["benchmark_dry_run"]["execution_contract"] == "artifact-only-external-job"
