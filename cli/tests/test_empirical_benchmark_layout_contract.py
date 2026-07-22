from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK = ROOT / "empirical_evidence/benchmarks/bl_ordo_018"
ASSETS = {
    "MODEL_1_API_RESULTS.zip",
    "MODEL_2_API_RESULTS.zip",
    "BLIND_SCORING_RESULTS.zip",
}


def test_bl_ordo_018_benchmark_evidence_has_one_canonical_location() -> None:
    assert not (ROOT / "evidence").exists()
    assert {path.name for path in BENCHMARK.glob("*.zip")} == ASSETS


def test_bl_ordo_018_benchmark_index_explains_the_retained_assets() -> None:
    readme = (BENCHMARK / "README.md").read_text(encoding="utf-8")
    for asset in ASSETS:
        assert asset in readme
    assert "M87_5_BL_ORDO_018_FINAL_CLOSURE_REPORT.json" in readme
