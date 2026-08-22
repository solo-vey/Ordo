
import importlib.util, tempfile, shutil, zipfile, io, base64, json
from pathlib import Path

spec=importlib.util.spec_from_file_location("editor_service_export",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

old=m.MODEL_CHAT_WORKSPACES
tmp=Path(tempfile.mkdtemp())
try:
    m.MODEL_CHAT_WORKSPACES=tmp
    root=m._workspace_root("s1")
    (root/"uploads"/"a.txt").write_text("hello",encoding="utf-8")
    payload={
      "debug":True,
      "session_id":"s1",
      "messages":[{"role":"user","content":"hi"},{"role":"assistant","content":"hello"}],
      "agent_trace":[{"iteration":1,"tool":{"name":"workspace.read","result":{"ok":True}}}],
      "usage_history":[{"prompt_tokens":10,"completion_tokens":2}],
      "attachments":[{"filename":"big.zip","media_type":"application/zip","size_bytes":123,"content_base64":"SECRET_BODY"}],
      "generated_files":[{"filename":"x.md","media_type":"text/markdown","size_bytes":4,"content_text":"BODY"}],
      "provider_info":{"provider":"custom","model":"m","base_url":"http://x","api_key":"MUST_NOT_EXPORT"},
      "errors":[]
    }
    out=m._model_chat_export(payload)
    assert out["media_type"]=="application/zip"
    raw=base64.b64decode(out["content_base64"])
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=set(z.namelist())
        required={"README.md","conversation.json","agent_trace.json","tool_calls.json","usage_history.json","workspace_head.json","workspace_index.json","attachments.json","generated_files.json","provider_info.json","errors.json","session.json"}
        assert required<=names
        provider=z.read("provider_info.json").decode()
        assert "MUST_NOT_EXPORT" not in provider and "api_key" not in provider
        attachments=z.read("attachments.json").decode()
        assert "SECRET_BODY" not in attachments
        generated=z.read("generated_files.json").decode()
        assert '"BODY"' not in generated
    plain=m._model_chat_export({"debug":False,"session_id":"s1","messages":payload["messages"]})
    assert plain["filename"].endswith(".md") and "## User" in plain["content_text"]
finally:
    m.MODEL_CHAT_WORKSPACES=old
    shutil.rmtree(tmp,ignore_errors=True)
print("PASS Model Chat Markdown/debug ZIP export and secret/body exclusion")
