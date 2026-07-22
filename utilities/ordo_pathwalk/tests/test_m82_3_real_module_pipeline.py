import json
from pathlib import Path

from utilities.ordo_pathwalk.runner.real_module_pipeline import run_real_module_pipeline

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "utilities/ordo_pathwalk/examples/m60_7_2_terminal_path_enumeration/source/program.ordo.yaml"


def test_generate_only_creates_cases_without_execution(tmp_path):
    out = tmp_path / "pipeline"
    result = run_real_module_pipeline(source_path=SOURCE, out_dir=out, mode="generate-only", case_set="clean")

    assert result["status"] == "generated"
    assert result["claims"]["testcases_generated"] is True
    assert result["claims"]["runtime_execution_performed"] is False
    assert result["execution"] == {}
    assert (out / "generation/clean_cases/SUMMARY.json").exists()
    assert not (out / "execution").exists()
    persisted = json.loads((out / "REAL_MODULE_PIPELINE_MANIFEST.json").read_text(encoding="utf-8"))
    assert persisted["schema_version"] == "ordo.pathwalk.real_module_pipeline.v1"


def test_generate_and_run_clean_suite_collects_evidence(tmp_path):
    out = tmp_path / "pipeline"
    result = run_real_module_pipeline(
        source_path=SOURCE,
        out_dir=out,
        mode="generate-and-run",
        case_set="clean",
        timeout_seconds=20,
        cleanup_policy="retain_all",
    )

    assert result["status"] == "passed"
    execution = result["execution"]["clean"]
    assert execution["job_count"] > 0
    assert execution["summary"]["status"] == "passed"
    assert execution["summary"]["counts"]["passed"] == execution["job_count"]
    assert all(item["return_code"] == 0 for item in execution["worker_launches"])
    assert result["claims"]["raw_execution_evidence_collected"] is True


def test_both_case_sets_are_generated(tmp_path):
    out = tmp_path / "pipeline"
    result = run_real_module_pipeline(
        source_path=SOURCE,
        out_dir=out,
        mode="generate-only",
        case_set="both",
        noise_patterns=["distraction"],
    )
    assert set(result["generation"]["suites"]) == {"clean", "noise"}
    assert (out / "generation/noise_cases/SUMMARY.json").exists()


def test_nonempty_output_requires_force(tmp_path):
    out = tmp_path / "pipeline"
    out.mkdir()
    (out / "sentinel").write_text("x", encoding="utf-8")
    try:
        run_real_module_pipeline(source_path=SOURCE, out_dir=out)
    except FileExistsError:
        pass
    else:
        raise AssertionError("expected FileExistsError")
