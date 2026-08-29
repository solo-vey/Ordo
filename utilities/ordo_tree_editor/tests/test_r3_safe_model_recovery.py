
import json
import pytest
from utilities.ordo_tree_editor import editor_service as es

def _semantic():
    return {
        "id":"G_X",
        "kind":"deterministic_gate",
        "execution_traits":{"runtime_executor":"deterministic_gate","model_executed":False,"model_executed_phases":[]},
        "semantic_source":{"condition":"state.x has unusual future syntax"},
        "state_contract":{"writes":[]},
        "routes":[{"key":"on_pass","target":"N_OK"},{"key":"on_fail","target":"N_BAD"}],
    }

def test_policy_defaults_to_automatic_safe():
    assert es._semantic_fallback_policy({}) == "automatic_safe"
    assert es._semantic_fallback_policy({"semantic_fallback_policy":"ask"}) == "ask"
    assert es._semantic_fallback_policy({"semantic_fallback_policy":"disabled"}) == "disabled"

def test_safe_recovery_can_choose_allowed_route_without_writes(monkeypatch):
    monkeypatch.setattr(es, "_package_context_for_record", lambda record: {"resolved_resources":[]})
    monkeypatch.setattr(es, "_provider_api_call", lambda credentials, system, context: (
        {}, {}, json.dumps({
            "status":"resolved","assistant_message":"","reason":"condition satisfied from canonical state",
            "state_patch":{"base_revision":0,"operations":[]},"next_id":"N_OK"
        }), {"input_tokens":1,"output_tokens":1,"total_tokens":2,"cached_tokens":0,"reasoning_tokens":0}
    ))
    out=es._safe_semantic_model_recovery(
        credentials={"provider":"test","model":"m","base_url":"x","api_style":"chat_completions"},
        record={"id":"G_X","condition":"future syntax"}, kind="gate", current_id="G_X", phase="enter",
        state={"x":1}, routes=[{"key":"on_pass","target":"N_OK"},{"key":"on_fail","target":"N_BAD"}],
        semantic_element=_semantic(), current_revision=0, failure_class="unsupported_mechanical_condition",
        failure_detail={"condition":"future syntax"},
    )
    assert out["next_id"]=="N_OK"
    assert out["debug"]["runtime"]["runtime_executor"]=="semantic_model_recovery"
    assert out["state"]=={"x":1}

def test_safe_recovery_rejects_unauthorized_target(monkeypatch):
    monkeypatch.setattr(es, "_package_context_for_record", lambda record: {"resolved_resources":[]})
    monkeypatch.setattr(es, "_provider_api_call", lambda credentials, system, context: (
        {}, {}, json.dumps({
            "status":"resolved","assistant_message":"","reason":"bad",
            "state_patch":{"base_revision":0,"operations":[]},"next_id":"N_HACK"
        }), {}
    ))
    with pytest.raises(ValueError, match="not allowed"):
        es._safe_semantic_model_recovery(
            credentials={"provider":"test","model":"m","base_url":"x","api_style":"chat_completions"},
            record={"id":"G_X"}, kind="gate", current_id="G_X", phase="enter",
            state={}, routes=[{"key":"on_pass","target":"N_OK"}],
            semantic_element=_semantic(), current_revision=0, failure_class="unsupported_runtime_executor",
            failure_detail={},
        )

def test_safe_recovery_needs_analyst_never_commits(monkeypatch):
    monkeypatch.setattr(es, "_package_context_for_record", lambda record: {"resolved_resources":[]})
    monkeypatch.setattr(es, "_provider_api_call", lambda credentials, system, context: (
        {}, {}, json.dumps({
            "status":"needs_analyst","assistant_message":"Need the missing value.","reason":"missing evidence",
            "state_patch":{"base_revision":0,"operations":[]},"next_id":None
        }), {}
    ))
    out=es._safe_semantic_model_recovery(
        credentials={"provider":"test","model":"m","base_url":"x","api_style":"chat_completions"},
        record={"id":"G_X"}, kind="gate", current_id="G_X", phase="enter",
        state={"x":None}, routes=[{"key":"on_pass","target":"N_OK"}],
        semantic_element=_semantic(), current_revision=0, failure_class="unsupported_mechanical_condition",
        failure_detail={},
    )
    assert out["await_analyst"] is True
    assert out["state"]=={"x":None}
