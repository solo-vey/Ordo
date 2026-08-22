#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,zipfile
from pathlib import Path

def included(root:Path,p:Path,out:Path)->bool:
    if not p.is_file(): return False
    if p.resolve()==out.resolve(): return False
    rel=p.relative_to(root).as_posix()
    if '__pycache__/' in rel or rel.endswith('.pyc'): return False
    return True

def main()->int:
    ap=argparse.ArgumentParser(description='Build a portable Vibe/Ordo package ZIP with derived compiled artifacts ordered after editable source so ordinary sequential extraction cannot make source appear newer than IR.')
    ap.add_argument('package_root'); ap.add_argument('output_zip')
    a=ap.parse_args(); root=Path(a.package_root).resolve(); out=Path(a.output_zip).resolve()
    if not root.is_dir():
        print(json.dumps({'status':'FAIL','code':'PACKAGE_ROOT_MISSING','path':str(root)})); return 2
    out.parent.mkdir(parents=True,exist_ok=True)
    files=[p for p in root.rglob('*') if included(root,p,out)]
    # ZIP extractors that do not restore member mtimes create files in archive order.
    # Keep derived compiled/ entries last so they cannot look older than their source solely due to extraction order.
    ordinary=sorted((p for p in files if not p.relative_to(root).as_posix().startswith('compiled/')),key=lambda p:p.relative_to(root).as_posix())
    compiled=sorted((p for p in files if p.relative_to(root).as_posix().startswith('compiled/')),key=lambda p:p.relative_to(root).as_posix())
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,allowZip64=True) as z:
        for p in ordinary+compiled:
            z.write(p,p.relative_to(root).as_posix())
    with zipfile.ZipFile(out) as z:
        bad=z.testzip(); names=z.namelist()
    status='PASS' if bad is None else 'FAIL'
    print(json.dumps({'status':status,'output':str(out),'files':len(names),'compiled_entries':len(compiled),'integrity_bad_member':bad},indent=2))
    return 0 if status=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
