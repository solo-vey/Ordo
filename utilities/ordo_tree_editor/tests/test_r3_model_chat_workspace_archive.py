
import importlib.util,tempfile,shutil,zipfile
from pathlib import Path
spec=importlib.util.spec_from_file_location("editor_service_archive",Path("editor_service.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
tmp=Path(tempfile.mkdtemp())
try:
    d=tmp/"generated_playbook/P";d.mkdir(parents=True)
    (d/"a.yaml").write_text("x: 1",encoding="utf-8")
    (d/"b.md").write_text("# B",encoding="utf-8")
    r=m._workspace_tool_execute(tmp,{"name":"workspace.archive","arguments":{"source":"generated_playbook/P","output":"generated/P.zip"}})
    assert r["ok"],r
    z=tmp/r["path"]
    assert z.is_file() and zipfile.is_zipfile(z)
    with zipfile.ZipFile(z) as archive:
        assert sorted(archive.namelist())==["a.yaml","b.md"]
finally:
    shutil.rmtree(tmp,ignore_errors=True)
print("PASS workspace.archive creates ZIP")
