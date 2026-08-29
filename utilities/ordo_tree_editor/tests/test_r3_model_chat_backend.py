import json, zipfile, io
from pathlib import Path
from utilities.ordo_tree_editor import editor_service as es


def test_model_chat_returns_files_and_bundle(monkeypatch):
    monkeypatch.setattr(es,"_live_credentials",lambda payload:{"provider":"test","model":"m","base_url":"x","api_style":"chat_completions"})
    payload={
        "answer_markdown":"Created.",
        "bundle_name":"demo.zip",
        "files":[
            {"filename":"source/program.ordo.yaml","media_type":"application/yaml","content_text":"title: Demo\nnodes: []\ngates: []\n"},
            {"filename":"README.md","media_type":"text/markdown","content_text":"# Demo\n"},
        ],
    }
    monkeypatch.setattr(es,"_provider_api_call",lambda credentials,system,context:({}, {}, json.dumps(payload), {}))
    out=es._model_chat({"messages":[{"role":"user","content":"create"}]})
    assert out["answer_markdown"]=="Created."
    assert any(x["filename"]=="source/program.ordo.yaml" for x in out["files"])
    bundle=next(x for x in out["files"] if x["filename"]=="demo.zip")
    raw=__import__('base64').b64decode(bundle["content_base64"])
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert "source/program.ordo.yaml" in z.namelist()


def test_model_chat_playbook_yaml_preview():
    source=Path("/tmp/rfp095/RISK_FACTOR_PASSPORT_PLAYBOOK_ALFA_0.9.5_DEV_R3COMPAT/source/program.ordo.yaml").read_text(encoding="utf-8")
    out=es._model_chat_playbook_preview({"filename":"program.ordo.yaml","content_text":source})
    assert out["graph"]["nodes"]
    assert any(n["id"]=="G_PASSPORT_CONSISTENCY" for n in out["graph"]["nodes"])
