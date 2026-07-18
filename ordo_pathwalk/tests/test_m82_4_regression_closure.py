import json
from pathlib import Path

import pytest

from ordo_pathwalk.runner import real_module_execution as runtime
from ordo_pathwalk.runner.real_module_pipeline import run_real_module_pipeline

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ordo_pathwalk/examples/m60_7_2_terminal_path_enumeration/source/program.ordo.yaml"
SUMMARY = ROOT / "ordo_pathwalk/examples/m60_7_3_clean_path_testcases/SUMMARY.json"


def test_pipeline_rejects_unknown_mode_and_case_set(tmp_path):
    with pytest.raises(ValueError, match="unsupported mode"):
        run_real_module_pipeline(source_path=SOURCE, out_dir=tmp_path / "a", mode="execute-anything")
    with pytest.raises(ValueError, match="unsupported case_set"):
        run_real_module_pipeline(source_path=SOURCE, out_dir=tmp_path / "b", case_set="unknown")


def test_pipeline_rejects_symlink_source(tmp_path):
    link = tmp_path / "program.ordo.yaml"
    link.symlink_to(SOURCE)
    with pytest.raises(ValueError, match="non-symlink"):
        run_real_module_pipeline(source_path=link, out_dir=tmp_path / "out")


def test_plan_rejects_duplicate_case_ids(tmp_path):
    package = tmp_path / "package"
    cases = package / "cases"
    cases.mkdir(parents=True)
    case_id = "DUPLICATE"
    case = {"case_id": case_id, "answer_steps": []}
    (cases / f"{case_id}.json").write_text(json.dumps(case), encoding="utf-8")
    summary = package / "SUMMARY.json"
    summary.write_text(json.dumps({"cases": [{"case_id": case_id}, {"case_id": case_id}]}), encoding="utf-8")
    with pytest.raises(runtime.InputRejected, match="duplicate case_id"):
        runtime.create_real_module_execution_plan(
            summary_path=summary,
            source_path=SOURCE,
            out_dir=tmp_path / "run",
        )


def test_plan_rejects_invalid_limits_and_cleanup_policy(tmp_path):
    with pytest.raises(runtime.InputRejected, match="timeout_seconds"):
        runtime.create_real_module_execution_plan(summary_path=SUMMARY, source_path=SOURCE, out_dir=tmp_path / "a", timeout_seconds=0)
    with pytest.raises(runtime.InputRejected, match="max_output_bytes"):
        runtime.create_real_module_execution_plan(summary_path=SUMMARY, source_path=SOURCE, out_dir=tmp_path / "b", max_output_bytes=10)
    with pytest.raises(runtime.InputRejected, match="cleanup_policy"):
        runtime.create_real_module_execution_plan(summary_path=SUMMARY, source_path=SOURCE, out_dir=tmp_path / "c", cleanup_policy="never")


def test_failure_taxonomy_covers_required_closure_scenarios():
    required = {
        "nonzero_exit",
        "terminated_by_signal",
        "watchdog_timeout",
        "missing_runtime_report",
        "malformed_runtime_report",
        "runtime_report_contract_mismatch",
        "input_validation",
        "result_exists",
        "spawn_failed",
        "stream_capture_failed",
        "cleanup_failed",
        "runner_failure",
    }
    assert required.issubset(runtime.FAILURE_CATEGORIES)
    assert set(runtime.STATUS_CLASS) == runtime.EXECUTION_STATUSES


def test_generate_and_run_manifest_has_bounded_claims(tmp_path):
    result = run_real_module_pipeline(
        source_path=SOURCE,
        out_dir=tmp_path / "pipeline",
        mode="generate-and-run",
        case_set="clean",
        timeout_seconds=20,
        cleanup_policy="cleanup_all",
    )
    assert result["status"] == "passed"
    assert result["claims"] == {
        "testcases_generated": True,
        "runtime_execution_performed": True,
        "raw_execution_evidence_collected": True,
        "scoring_performed": False,
        "calibration_performed": False,
    }
    assert result["execution"]["clean"]["summary"]["counts"]["invalid_results"] == 0
