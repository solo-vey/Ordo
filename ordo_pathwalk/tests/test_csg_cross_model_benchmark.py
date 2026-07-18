import json
from pathlib import Path

from ordo_pathwalk.runner.csg_benchmark import aggregate_cross_model_scores


def _score(path: Path, provider: str, name: str, status: str = "passed", dataset: str = "M74.3-csg-benchmark-v1"):
    path.write_text(json.dumps({
        "model": {"provider": provider, "name": name},
        "status": status,
        "real_model_evidence": True,
        "dataset_version": dataset,
        "metrics": {"overall_classification_accuracy": 1.0},
    }), encoding="utf-8")


def test_cross_model_gate_blocks_single_target_single_run(tmp_path: Path):
    _score(tmp_path / "run1.json", "OpenAI", "GPT-5.6 Thinking")
    result = aggregate_cross_model_scores(tmp_path)
    assert result["status"] == "blocked"
    codes = {b["code"] for b in result["blockers"]}
    assert "CSG_MODEL_TARGET_COUNT_INSUFFICIENT" in codes
    assert "CSG_REPEAT_RUN_COUNT_INSUFFICIENT" in codes


def test_cross_model_gate_passes_three_targets_two_runs_each(tmp_path: Path):
    targets = [("OpenAI", "A"), ("Anthropic", "B"), ("Google", "C")]
    for i, (provider, name) in enumerate(targets):
        _score(tmp_path / f"{i}_1.json", provider, name)
        _score(tmp_path / f"{i}_2.json", provider, name)
    result = aggregate_cross_model_scores(tmp_path)
    assert result["status"] == "passed"
    assert result["distinct_model_target_count"] == 3
    assert result["gates"]["G_CSG_CROSS_MODEL_BENCHMARK_READY"] == "passed"


def test_cross_model_gate_blocks_failed_run(tmp_path: Path):
    targets = [("OpenAI", "A"), ("Anthropic", "B"), ("Google", "C")]
    for i, (provider, name) in enumerate(targets):
        _score(tmp_path / f"{i}_1.json", provider, name)
        _score(tmp_path / f"{i}_2.json", provider, name, status="blocked" if i == 1 else "passed")
    result = aggregate_cross_model_scores(tmp_path)
    assert result["status"] == "blocked"
    assert any(b["code"] == "CSG_TARGET_HAS_FAILED_RUN" for b in result["blockers"])
