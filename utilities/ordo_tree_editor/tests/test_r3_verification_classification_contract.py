
import json
from utilities.ordo_tree_editor import editor_service as es

def test_invalid_model_classification_is_normalized(monkeypatch):
    package={"id":"p","source":{},"semantic_plan":{"interaction_contract":{"locale":"uk-UA","model_output_language":"uk"}}}
    es.PLAYBOOK_PACKAGES["p"]=package
    monkeypatch.setattr(es,"_live_credentials",lambda payload:{"provider":"test","model":"m","base_url":"x","api_style":"chat_completions"})
    monkeypatch.setattr(es,"_provider_api_call",lambda credentials,system,context:(
        {},{},json.dumps({"explanation":"x","classification":"state"}),{}
    ))
    result=es._model_explanation({"package_id":"p","kind":"verification_check","verification_check":{"id":"x","status":"FAIL","output":"x"}})
    assert result["classification"]=="inconclusive"
    assert result["classification_normalized_from"]=="state"

def test_valid_model_classification_is_preserved(monkeypatch):
    package={"id":"q","source":{},"semantic_plan":{"interaction_contract":{"locale":"uk-UA","model_output_language":"uk"}}}
    es.PLAYBOOK_PACKAGES["q"]=package
    monkeypatch.setattr(es,"_live_credentials",lambda payload:{"provider":"test","model":"m","base_url":"x","api_style":"chat_completions"})
    monkeypatch.setattr(es,"_provider_api_call",lambda credentials,system,context:(
        {},{},json.dumps({"explanation":"x","classification":"verification_tool_defect"}),{}
    ))
    result=es._model_explanation({"package_id":"q","kind":"verification_check","verification_check":{"id":"x","status":"FAIL","output":"x"}})
    assert result["classification"]=="verification_tool_defect"
