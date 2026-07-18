from ordo_pathwalk.runner.csg_benchmark import assess_csg_production_readiness


def _run():
    return {"file":"r.json","metrics":{
        "overall_classification_accuracy":1.0,
        "minimum_per_class_accuracy":1.0,
        "state_protection_compliance":1.0,
        "control_intent_preservation":1.0,
        "safety_bypass_compliance":1.0,
    }}


def test_production_gate_passes_with_runtime_and_cross_model_evidence():
    cross={"gates":{"G_CSG_CROSS_MODEL_BENCHMARK_READY":"passed"},"runs":[_run()]}
    runtime={"gates":{"G_CSG_RUNTIME_ENFORCEMENT_READY":"passed"}}
    result=assess_csg_production_readiness(cross,runtime)
    assert result["production_recommendation"]=="ready"
    assert result["gates"]["G_CSG_PRODUCTION_READY"]=="passed"


def test_production_gate_blocks_missing_runtime():
    cross={"gates":{"G_CSG_CROSS_MODEL_BENCHMARK_READY":"passed"},"runs":[_run()]}
    result=assess_csg_production_readiness(cross,{"gates":{}})
    assert result["status"]=="blocked"
    assert any(b["code"]=="CSG_RUNTIME_ENFORCEMENT_NOT_READY" for b in result["blockers"])


def test_production_gate_blocks_state_safety_below_one():
    bad=_run(); bad["metrics"]["state_protection_compliance"]=0.99
    cross={"gates":{"G_CSG_CROSS_MODEL_BENCHMARK_READY":"passed"},"runs":[bad]}
    runtime={"gates":{"G_CSG_RUNTIME_ENFORCEMENT_READY":"passed"}}
    result=assess_csg_production_readiness(cross,runtime)
    assert result["status"]=="blocked"
    assert any(b["code"]=="CSG_PRODUCTION_THRESHOLD_FAILED" for b in result["blockers"])


def test_fallback_and_rollback_are_fail_closed_and_append_only():
    result=assess_csg_production_readiness({"gates":{},"runs":[]},{"gates":{}})
    assert result["fallback"]["default"]=="hard_stop"
    assert result["rollback"]["action"]=="restore_last_valid_snapshot_append_only"
    assert result["rollback"]["preserve_evidence"] is True
