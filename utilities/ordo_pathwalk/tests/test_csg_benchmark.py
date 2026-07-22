import json
from pathlib import Path

from utilities.ordo_pathwalk.runner.csg_benchmark import build_dataset, score_evidence, CANONICAL_CLASSES


def _evidence(dataset, *, provider="openai", wrong_case=None, mutate_case=None):
    predictions = []
    for case in dataset["cases"]:
        expected = case["expected"]
        predictions.append({
            "case_id": case["case_id"],
            "classification": "unrelated_topic" if case["case_id"] == wrong_case else expected["classification"],
            "action": expected["action"],
            "state_mutation_performed": case["case_id"] == mutate_case,
            "protected_state_changed": case["case_id"] == mutate_case,
        })
    return {
        "benchmark_mode": "live-model",
        "model": {"provider": provider, "name": "test-model", "driver": "api-driver"},
        "predictions": predictions,
    }


def test_dataset_covers_every_canonical_class_twice(tmp_path: Path):
    path = tmp_path / "dataset.json"
    dataset = build_dataset(path)
    counts = {name: 0 for name in CANONICAL_CLASSES}
    for case in dataset["cases"]:
        counts[case["expected"]["classification"]] += 1
    assert path.exists()
    assert all(value >= 2 for value in counts.values())


def test_perfect_real_model_evidence_passes(tmp_path: Path):
    dataset_path = tmp_path / "dataset.json"
    dataset = build_dataset(dataset_path)
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(_evidence(dataset)), encoding="utf-8")
    result = score_evidence(dataset_path, evidence_path)
    assert result["status"] == "passed"
    assert result["gates"]["G_CSG_MODEL_BENCHMARK_READY"] == "passed"


def test_synthetic_evidence_never_passes_empirical_gate(tmp_path: Path):
    dataset_path = tmp_path / "dataset.json"
    dataset = build_dataset(dataset_path)
    evidence = _evidence(dataset, provider="offline")
    evidence["benchmark_mode"] = "synthetic"
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
    result = score_evidence(dataset_path, evidence_path)
    assert result["status"] == "blocked"
    assert result["real_model_evidence"] is False
    assert any(v["code"] == "CSG_REAL_MODEL_EVIDENCE_REQUIRED" for v in result["violations"])


def test_state_mutation_violation_blocks_gate(tmp_path: Path):
    dataset_path = tmp_path / "dataset.json"
    dataset = build_dataset(dataset_path)
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(_evidence(dataset, mutate_case="CSG-UNRELATED-01")), encoding="utf-8")
    result = score_evidence(dataset_path, evidence_path)
    assert result["status"] == "blocked"
    assert result["metrics"]["state_protection_compliance"] < 1.0
