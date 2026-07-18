import json
from pathlib import Path
import pytest
import yaml
from ordo.delivery_target import recommend_delivery_target, record_delivery_target_decision

ROOT = Path(__file__).resolve().parents[2]

def low_risk():
    return {"risk_level":"low","branch_count":2,"gate_count":1,"backtrack_point_count":1,"prompt_evidence":{"runs":3,"composite_score":94,"branch_score":90,"backtrack_score":88}}

def test_prompt_only_recommended_when_thresholds_pass():
    assert recommend_delivery_target(low_risk())["recommended_target"] == "prompt_only"

def test_engine_is_safe_default_for_missing_evidence():
    r=recommend_delivery_target({"risk_level":"low"})
    assert r["recommended_target"] == "engine_runtime"
    assert r["safe_default"] == "engine_runtime"

def test_high_risk_requires_engine():
    a=low_risk(); a["risk_level"]="high"
    assert recommend_delivery_target(a)["recommended_target"] == "engine_runtime"

def test_both_may_be_recommended_after_thresholds():
    a=low_risk(); a["deliver_both_requested"]=True
    assert recommend_delivery_target(a)["recommended_target"] == "both"

def test_analyst_can_confirm_recommendation():
    r=recommend_delivery_target(low_risk())
    d=record_delivery_target_decision(r,"prompt_only",analyst_id="A1")
    assert d["status"] == "confirmed" and d["package_outputs"]["prompt_only"]

def test_unsafe_prompt_override_is_blocked():
    r=recommend_delivery_target({"risk_level":"critical"})
    assert record_delivery_target_decision(r,"prompt_only")["status"] == "blocked_prompt_only_override"

def test_invalid_target_rejected():
    with pytest.raises(ValueError): record_delivery_target_decision(recommend_delivery_target(low_risk()),"invalid")

def test_apf_contains_decision_gate_before_handoff():
    p=ROOT/'packages/ordo_applied_project_factory/source/program.ordo.yaml'
    data=yaml.safe_load(p.read_text())
    ids=[n['id'] for n in data['nodes']]
    assert ids.index('N_SHARED_TAIL_DELIVERY_TARGET_DECISION') < ids.index('N_SHARED_TAIL_HANDOFF_PACKAGE_GENERATION')
    node=next(n for n in data['nodes'] if n['id']=='N_SHARED_TAIL_DELIVERY_TARGET_DECISION')
    assert node['recommendation_contract']['safe_default']=='engine_runtime'
    assert set(node['allowed_answers'])=={'engine_runtime','prompt_only','both'}

def test_schema_and_documentation_exist():
    assert (ROOT/'language/schemas/arf_delivery_target_decision.schema.json').is_file()
    assert (ROOT/'docs/ARF_DELIVERY_TARGET_DECISION_GATE.md').is_file()
    assert (ROOT/'book/en/chapters/chapter_83_delivery_target_decision.md').is_file()
