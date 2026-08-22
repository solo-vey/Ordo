
import importlib.util, io, zipfile
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_zip_compaction",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

buf=io.BytesIO()
with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
    z.writestr("docs/README.md","readme body")
    z.writestr("PROMPT_START.md","START PROMPT BODY")
    for i in range(20):
        z.writestr(f"docs/file_{i}.md","x"*10000)

result=m._compact_model_chat_zip(buf.getvalue(),"playbook.zip")
assert result["workspace_summary"]["files"]==22
assert len(result["archive_index"])==22
assert len(result["entrypoint_context"])<=6
paths=[x["path"] for x in result["entrypoint_context"]]
assert "PROMPT_START.md" in paths
embedded=sum(len(x["content_text"]) for x in result["entrypoint_context"])
assert embedded < 150000
assert "archive_text_files" not in result
print("PASS ZIP workspace index + bounded entrypoint context")
