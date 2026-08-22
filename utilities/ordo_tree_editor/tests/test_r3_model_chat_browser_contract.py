
import importlib.util, tempfile, shutil
from pathlib import Path

spec=importlib.util.spec_from_file_location("editor_service_browser_contract",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

old_live=m._live_credentials
old_agent=m._model_chat_agent_loop
old_root=m.MODEL_CHAT_WORKSPACES
tmp=Path(tempfile.mkdtemp())
try:
    m.MODEL_CHAT_WORKSPACES=tmp
    m._live_credentials=lambda payload: {"provider":"custom","model":"test","api_style":"chat_completions"}
    captured={}
    def fake_agent(credentials,root,user_message,history,max_iterations=12,activity_callback=None,cancel_check=None):
        captured["user_message"]=user_message
        captured["history"]=history
        captured["session_root"]=root
        return "Привіт!",[],{"prompt_tokens":1,"completion_tokens":1,"total_tokens":2},[]
    m._model_chat_agent_loop=fake_agent

    payload={
      "session_id":"browser-session-1",
      "messages":[
        {"role":"assistant","content":"old answer","files":[]},
        {"role":"user","content":"привіт","files":[]}
      ],
      "attachments":[]
    }
    out=m._model_chat(payload)
    assert out["status"]=="passed"
    assert out["answer_markdown"]=="Привіт!"
    assert captured["user_message"]=="привіт"
    assert captured["history"]==[{"role":"assistant","content":"old answer"}]
    assert captured["session_root"].name=="browser-session-1"
finally:
    m._live_credentials=old_live
    m._model_chat_agent_loop=old_agent
    m.MODEL_CHAT_WORKSPACES=old_root
    shutil.rmtree(tmp,ignore_errors=True)
print("PASS exact browser Model Chat payload remains compatible with agent backend")
