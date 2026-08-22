from pathlib import Path
from utilities.ordo_tree_editor import editor_service as es


def test_model_chat_returns_workspace_files(monkeypatch, tmp_path):
    monkeypatch.setattr(es,"_live_credentials",lambda payload:{"provider":"test","model":"m","base_url":"x","api_style":"chat_completions"})
    monkeypatch.setattr(es,"_workspace_root",lambda session_id:tmp_path)
    def loop(credentials, root, user_message, history, **kwargs):
        output=root / "source" / "program.ordo.yaml"
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text("nodes: []\ngates: []\n",encoding="utf-8")
        return "Created.", [], {}, []
    monkeypatch.setattr(es,"_model_chat_agent_loop",loop)
    out=es._model_chat({"messages":[{"role":"user","content":"create"}]})
    assert out["answer_markdown"]=="Created."
    assert any(x["filename"]=="source/program.ordo.yaml" for x in out["files"])


def test_model_chat_playbook_yaml_preview():
    source="""nodes:
  - id: N_START
    question: Start.
gates:
  - id: G_CONSISTENCY
    condition: state.ready == true
"""
    out=es._model_chat_playbook_preview({"filename":"program.ordo.yaml","content_text":source})
    assert out["graph"]["nodes"]
    assert any(n["id"]=="G_CONSISTENCY" for n in out["graph"]["nodes"])
