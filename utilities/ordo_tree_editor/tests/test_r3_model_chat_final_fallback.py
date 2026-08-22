
import json
from utilities.ordo_tree_editor import editor_service as es

def _creds(_):
    return {"provider":"test","model":"m","base_url":"x","api_style":"chat_completions"}

def test_model_chat_accepts_message_alias(monkeypatch):
    monkeypatch.setattr(es,"_live_credentials",_creds)
    monkeypatch.setattr(es,"_provider_api_call",lambda *args,**kwargs: ({},{},json.dumps({"kind":"final","message":"Привіт!"}),{}))
    out=es._model_chat({"messages":[{"role":"user","content":"привіт"}]})
    assert out["answer_markdown"]=="Привіт!"

def test_model_chat_accepts_plain_text_final(monkeypatch):
    monkeypatch.setattr(es,"_live_credentials",_creds)
    monkeypatch.setattr(es,"_provider_api_call",lambda *args,**kwargs: ({},{},"Hello from model",{}))
    out=es._model_chat({"messages":[{"role":"user","content":"hello"}]})
    assert out["answer_markdown"]=="Hello from model"
