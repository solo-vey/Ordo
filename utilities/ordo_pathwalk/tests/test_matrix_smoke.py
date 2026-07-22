from pathlib import Path

from utilities.ordo_pathwalk.runner.matrix_smoke import run_matrix_smoke


def test_matrix_smoke_generates_score_and_summary(tmp_path: Path):
    summary = run_matrix_smoke(
        tmp_path / "matrix",
        depth=1,
        branching=(2, 2),
        tree_seed=7,
        script_seed=8,
        runtime_views=("json",),
        force=True,
    )
    assert summary["status"] == "ok"
    assert summary["matrix_smoke"]["status"] == "passed"
    assert summary["gate_pass_rate"] == 1.0
    assert (tmp_path / "matrix" / "scores" / "SUMMARY.json").exists()
    assert (tmp_path / "matrix" / "scores" / "scenario_000_json_score.json").exists()
