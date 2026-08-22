#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

def run(cmd, root):
    p=subprocess.run(cmd,cwd=root,text=True,capture_output=True)
    return {'cmd':' '.join(cmd),'status':'PASS' if p.returncode==0 else 'FAIL','returncode':p.returncode,'stdout':p.stdout[-4000:],'stderr':p.stderr[-2000:]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package_root'); a=ap.parse_args(); root=Path(a.package_root).resolve()
    checks=[]
    candidates=[
      ('tools/validate_authoring_information_model.py',[sys.executable,'tools/validate_authoring_information_model.py','.']),
      ('tools/validate_information_projection.py',[sys.executable,'tools/validate_information_projection.py','.','--playbook','source','--require-bound']),
      ('tools/validate_reusable_authoring_templates.py',[sys.executable,'tools/validate_reusable_authoring_templates.py','.']),
      ('tools/validate_artifact_materialization_registry.py',[sys.executable,'tools/validate_artifact_materialization_registry.py','.']),
      ('tools/verify_execution_responsibility_map.py',[sys.executable,'tools/verify_execution_responsibility_map.py']),
    ]
    for rel,cmd in candidates:
        if (root/rel).exists(): checks.append(run(cmd,root))
    # Required structural surfaces for a production-editable generated playbook.
    req=['source','authoring','verification','tools']
    missing=[x for x in req if not (root/x).exists()]
    checks.append({'cmd':'required_surfaces','status':'PASS' if not missing else 'FAIL','missing':missing})
    ok=all(x['status']=='PASS' for x in checks)
    out={'status':'PASS' if ok else 'FAIL','eligible_for_scoring':ok,'checks':checks}
    print(json.dumps(out,ensure_ascii=False,indent=2)); return 0 if ok else 1
if __name__=='__main__': raise SystemExit(main())
