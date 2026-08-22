
import importlib.util, tempfile, shutil
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_agent_workspace",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

tmp=Path(tempfile.mkdtemp())
try:
    (tmp/"uploads").mkdir();(tmp/"generated").mkdir();(tmp/"extracted").mkdir();(tmp/"tmp").mkdir()
    (tmp/"uploads"/"START_PROMPT.md").write_text("begin here",encoding="utf-8")
    assert m._workspace_tool_execute(tmp,{"name":"workspace.list","arguments":{"path":"uploads"}})["ok"]
    s=m._workspace_tool_execute(tmp,{"name":"workspace.search","arguments":{"query":"START_PROMPT"}})
    assert s["results"] and s["results"][0]["path"].endswith("START_PROMPT.md")
    r=m._workspace_tool_execute(tmp,{"name":"workspace.read","arguments":{"path":"uploads/START_PROMPT.md"}})
    assert r["content"]=="begin here"
    w=m._workspace_tool_execute(tmp,{"name":"workspace.write","arguments":{"path":"generated/result.md","content":"done"}})
    assert w["ok"] and (tmp/"generated/result.md").exists()
finally:
    shutil.rmtree(tmp)
print("PASS persistent workspace tool registry")
