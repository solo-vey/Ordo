
import importlib.util, tempfile, shutil
from pathlib import Path

spec=importlib.util.spec_from_file_location("editor_service_path_positive",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

old_active=m._active_playbook_package
old_runtime=m._runtime_workspace
tmp=Path(tempfile.mkdtemp())
try:
    p=tmp/"reports/runtime/validation_report.json"
    p.parent.mkdir(parents=True)
    p.write_text('{"status":"PASS"}',encoding="utf-8")
    m._active_playbook_package=lambda: {"resources":{}}
    m._runtime_workspace=lambda: tmp
    out=m._package_context_for_record({"report_ref":"reports/runtime/validation_report.json"})
    assert len(out["resolved_resources"])==1
    item=out["resolved_resources"][0]
    assert item["reason"]=="runtime_artifact"
    assert item["path"]=="reports/runtime/validation_report.json"
    assert '"PASS"' in item["content"]
finally:
    m._active_playbook_package=old_active
    m._runtime_workspace=old_runtime
    shutil.rmtree(tmp,ignore_errors=True)
print("PASS valid runtime resource resolution remains functional")
