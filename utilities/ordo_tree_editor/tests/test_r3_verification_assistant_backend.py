
import json
from utilities.ordo_tree_editor import editor_service as es

def test_verification_assistant_is_read_only(monkeypatch):
    source={"nodes":[],"gates":[]}
    package={"id":"verify-chat","source":source,"semantic_plan":{"interaction_contract":{"locale":"uk-UA","model_output_language":"uk"}}}
    es.PLAYBOOK_PACKAGES["verify-chat"]=package
    monkeypatch.setattr(es,"_live_credentials",lambda payload:{"provider":"test","model":"m","base_url":"x","api_style":"chat_completions"})
    monkeypatch.setattr(es,"_provider_api_call",lambda credentials,system,context:(
        {},{},json.dumps({"explanation":"Причина пропуску — відсутні runtime evidence."}),{}
    ))
    result=es._verification_assistant({
        "package_id":"verify-chat",
        "verification_check":{"id":"validate_state","status":"SKIPPED","skip_label":"Needs runtime evidence","message":"No runtime state."},
        "messages":[{"role":"user","content":"Чому пропущено?"}]
    })
    assert "runtime" in result["answer_markdown"]
    assert source=={"nodes":[],"gates":[]}

def test_pass_check_not_discussable(monkeypatch):
    package={"id":"verify-pass","source":{},"semantic_plan":{"interaction_contract":{"locale":"en-US","model_output_language":"en"}}}
    es.PLAYBOOK_PACKAGES["verify-pass"]=package
    monkeypatch.setattr(es,"_live_credentials",lambda payload:{"provider":"test","model":"m","base_url":"x","api_style":"chat_completions"})
    try:
        es._verification_assistant({
            "package_id":"verify-pass",
            "verification_check":{"id":"lint","status":"PASS"},
            "messages":[{"role":"user","content":"Discuss"}]
        })
    except ValueError as exc:
        assert "non-PASS" in str(exc)
    else:
        raise AssertionError("PASS check discussion must be rejected")


def test_verification_assistant_rejects_empty_model_payload(monkeypatch):
    package={"id":"verify-empty","source":{},"semantic_plan":{"interaction_contract":{"locale":"uk-UA","model_output_language":"uk"}}}
    es.PLAYBOOK_PACKAGES["verify-empty"]=package
    monkeypatch.setattr(es,"_live_credentials",lambda payload:{"provider":"test","model":"m","base_url":"x","api_style":"chat_completions"})
    monkeypatch.setattr(es,"_provider_api_call",lambda credentials,system,context:(
        {},{},json.dumps({"explanation":""}),{}
    ))
    try:
        es._verification_assistant({
            "package_id":"verify-empty",
            "verification_check":{"id":"lint","status":"FAIL","message":"lint failed"},
            "messages":[{"role":"user","content":"What happened?"}]
        })
    except ValueError as exc:
        assert "no non-empty" in str(exc)
    else:
        raise AssertionError("empty model response must fail visibly")
