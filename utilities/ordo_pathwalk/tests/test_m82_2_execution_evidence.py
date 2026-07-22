import json
from pathlib import Path

from utilities.ordo_pathwalk.runner import real_module_execution as runtime

ROOT = Path(__file__).resolve().parents[3]
SUMMARY = ROOT / "utilities/ordo_pathwalk/examples/m60_7_3_clean_path_testcases/SUMMARY.json"
SOURCE = ROOT / "utilities/ordo_pathwalk/examples/m60_7_2_terminal_path_enumeration/source/program.ordo.yaml"


def _plan(tmp_path: Path, **kwargs):
    out = tmp_path / "run"
    plan = runtime.create_real_module_execution_plan(
        summary_path=SUMMARY,
        source_path=SOURCE,
        out_dir=out,
        timeout_seconds=20,
        **kwargs,
    )
    return out, plan


def test_taxonomy_is_closed_and_status_classes_are_total():
    assert set(runtime.STATUS_CLASS) == runtime.EXECUTION_STATUSES
    assert None in runtime.FAILURE_CATEGORIES
    assert "watchdog_timeout" in runtime.FAILURE_CATEGORIES
    assert "malformed_runtime_report" in runtime.FAILURE_CATEGORIES
    assert "terminated_by_signal" in runtime.FAILURE_CATEGORIES


def test_passed_job_persists_versioned_valid_evidence(tmp_path):
    out, plan = _plan(tmp_path, cleanup_policy="retain_all")
    job = plan["jobs"][0]
    result = runtime.run_real_module_execution_job(out / "REAL_MODULE_EXECUTION_PLAN.json", job["job_id"])

    assert result["schema_version"] == runtime.SCHEMA_RESULT
    assert result["milestone"] == "M82.2"
    evidence = result["evidence"]
    assert evidence["schema_version"] == runtime.SCHEMA_EVIDENCE
    assert evidence["outcome"] == {
        "status": "passed",
        "status_class": "success",
        "failure_category": None,
        "retryable": False,
        "testcase_decision": "pass",
    }
    assert evidence["linkage"]["job_id"] == job["job_id"]
    assert evidence["claims"]["raw_evidence_only"] is True
    assert runtime.validate_execution_evidence(evidence) == []


def test_invalid_output_taxonomy_distinguishes_missing_and_malformed_report():
    assert runtime._classify_failure(status="invalid_output", return_code=0, report_status="missing") == "missing_runtime_report"
    assert runtime._classify_failure(status="invalid_output", return_code=0, report_status="invalid:JSONDecodeError") == "malformed_runtime_report"
    assert runtime._classify_failure(status="invalid_output", return_code=0, report_status="unexpected") == "runtime_report_contract_mismatch"


def test_process_failure_taxonomy_distinguishes_exit_and_signal():
    assert runtime._classify_failure(status="process_failed", return_code=2, report_status="missing") == "nonzero_exit"
    assert runtime._classify_failure(status="process_failed", return_code=-9, report_status="missing") == "terminated_by_signal"


def test_evidence_validator_rejects_contradictory_success():
    evidence = {
        "schema_version": runtime.SCHEMA_EVIDENCE,
        "linkage": {"job_id": "EXEC_X"},
        "outcome": {"status": "passed", "status_class": "success", "failure_category": "nonzero_exit"},
        "process": {},
        "diagnostics": {},
        "claims": {"raw_evidence_only": True},
    }
    errors = runtime.validate_execution_evidence(evidence)
    assert "passed evidence must not have failure_category" in errors


def test_collector_rejects_tampered_v3_evidence(tmp_path):
    out, plan = _plan(tmp_path, cleanup_policy="retain_all")
    job = plan["jobs"][0]
    runtime.run_real_module_execution_job(out / "REAL_MODULE_EXECUTION_PLAN.json", job["job_id"])
    result_path = Path(job["result_path"])
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["evidence"]["outcome"]["status_class"] = "process"
    result_path.write_text(json.dumps(result), encoding="utf-8")

    summary = runtime.collect_real_module_execution_results(out / "REAL_MODULE_EXECUTION_PLAN.json")
    assert summary["schema_version"] == runtime.SCHEMA_SUMMARY
    assert summary["counts"]["invalid_results"] == 1
    assert summary["counts"]["collected"] == 0
    assert "status_class does not match status" in summary["invalid_results"][0]["reason"]
