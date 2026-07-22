import json
from pathlib import Path

from utilities.ordo_pathwalk.runner.aggregate import aggregate


def test_aggregate_breaks_down_runtime_view(tmp_path: Path):
    (tmp_path / "a_score.json").write_text(json.dumps({"gate_passed": True, "path_quality_score": 1.0, "runtime_view": "json"}))
    (tmp_path / "b_score.json").write_text(json.dumps({"gate_passed": True, "path_quality_score": 0.5, "runtime_view": "ordo-code"}))
    summary = aggregate(tmp_path)
    assert summary["gate_pass_rate"] == 1.0
    assert summary["breakdown_by_runtime_view"]["json"]["mean"] == 1.0
    assert summary["breakdown_by_runtime_view"]["ordo-code"]["mean"] == 0.5


def test_aggregate_no_scores(tmp_path: Path):
    assert aggregate(tmp_path)["status"] == "no_scores_found"
