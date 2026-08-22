
import importlib.util,tempfile,shutil
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_changed",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
tmp=Path(tempfile.mkdtemp())
try:
    (tmp/"uploads").mkdir();(tmp/"uploads/in.txt").write_text("source",encoding="utf-8")
    before=m._workspace_file_snapshot(tmp)
    out=tmp/"generated_playbook/P/program.ordo.yaml";out.parent.mkdir(parents=True);out.write_text("name: P",encoding="utf-8")
    changed=[p.relative_to(tmp).as_posix() for p in m._workspace_changed_files(tmp,before)]
    assert changed==["generated_playbook/P/program.ordo.yaml"],changed
finally:
    shutil.rmtree(tmp,ignore_errors=True)
print("PASS changed generated files are surfaced outside generated/")
