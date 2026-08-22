
import importlib.util, tempfile, shutil, json, math
from pathlib import Path

spec=importlib.util.spec_from_file_location("editor_service_workspace_head",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

tmp=Path(tempfile.mkdtemp())
try:
    (tmp/"uploads").mkdir()
    (tmp/"extracted/pkg/docs").mkdir(parents=True)
    (tmp/"extracted/pkg/PROMPTS").mkdir(parents=True)
    (tmp/"generated").mkdir()
    (tmp/"tmp").mkdir()
    (tmp/"extracted/pkg/START_PROMPT.md").write_text("START BODY MUST NOT APPEAR IN HEAD",encoding="utf-8")
    (tmp/"extracted/pkg/README.md").write_text("README BODY MUST NOT APPEAR IN HEAD",encoding="utf-8")
    for i in range(5000):
        (tmp/"extracted/pkg/docs"/f"file_{i:05d}.md").write_text("x",encoding="utf-8")
    head=m._workspace_head(tmp)
    encoded=json.dumps(head,ensure_ascii=False)
    assert head["files"]==5002
    assert len(head["entrypoint_candidates"])<=6
    assert any("START_PROMPT.md" in p for p in head["entrypoint_candidates"])
    assert "START BODY" not in encoded and "README BODY" not in encoded
    # Conservative mixed-language estimate; must stay comfortably below review's 400-token section.
    estimated=math.ceil(len(encoded)/3.2)
    assert estimated < 400,(estimated,len(encoded),encoded)
finally:
    shutil.rmtree(tmp,ignore_errors=True)
print("PASS workspace_head stays compact with 5000-file workspace")
