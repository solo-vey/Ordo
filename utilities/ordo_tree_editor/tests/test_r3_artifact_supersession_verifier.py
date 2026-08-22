import importlib.util
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"verify_release_evidence_v3.py"
spec=importlib.util.spec_from_file_location("v",P)
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)

def base_summary(freshness):
    return {
      "evidence_profile":"live",
      "provenance":{"live_calls":1,"replayed_calls":0},
      "provider_capability_profile":{"status":"recorded","supports_json_schema":True},
      "usage":{"calls":1},
      "accounting":{"provider_attempts":1,"token_baseline_attempts":1},
      "retry_quality":{"retry_histogram":{"1":1},"acceptance_pass":True,"exhausted_retry_budget":0},
      "run":{"status":"completed","llm_calls":1,"outcome":{"reason":"terminal","nodeId":"END"},
             "step_class_counts":{"live_model_call":1},
             "run_journal":{"artifact_freshness":freshness}}}

def test_older_stale_materialization_is_superseded_by_new_fresh_one():
    s=base_summary([
      {"path":"a.md","materialized_from_revision":2,"freshness_status":"stale"},
      {"path":"a.md","materialized_from_revision":4,"freshness_status":"fresh"},
    ])
    out=v.verify(s,{},"END",True)
    assert out["status"]=="PASS", out

def test_latest_stale_materialization_still_fails_closed():
    s=base_summary([
      {"path":"a.md","materialized_from_revision":2,"freshness_status":"fresh"},
      {"path":"a.md","materialized_from_revision":4,"freshness_status":"stale"},
    ])
    out=v.verify(s,{},"END",True)
    assert out["status"]=="FAIL"
    assert any(c["id"]=="NO_STALE_ARTIFACTS" and c["status"]=="FAIL" for c in out["checks"])
