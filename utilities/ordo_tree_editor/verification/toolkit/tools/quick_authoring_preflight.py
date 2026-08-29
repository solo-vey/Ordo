#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,time,json,os
R=Path(__file__).resolve().parents[1]
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
steps=[
 ('portable_integrity',[sys.executable,str(R/'tools/verify_portable_authoring_bundle.py'),str(R)]),
 ('lint',[sys.executable,str(R/'tools/ordo_authoring.py'),'lint',str(R/'source/program.ordo.yaml')]),
 ('compile',[sys.executable,str(R/'tools/ordo_authoring.py'),'compile',str(R)]),
 ('test',[sys.executable,str(R/'tools/ordo_authoring.py'),'test',str(R)]),
 ('coverage',[sys.executable,str(R/'tools/ordo_authoring.py'),'coverage',str(R)]),
 ('clean_check',[sys.executable,str(R/'tools/ordo_authoring.py'),'clean-check',str(R),'--profile','strict'])
]
results=[]; t0=time.monotonic()
for name,cmd in steps:
    t=time.monotonic(); p=subprocess.run(cmd,capture_output=True,text=True,env=env)
    results.append({'id':name,'status':'PASS' if p.returncode==0 else 'FAIL','seconds':round(time.monotonic()-t,3),'tail':(p.stdout+p.stderr)[-500:]})
status='PASS' if all(x['status']=='PASS' for x in results) else 'FAIL'
out={'schema_version':'1.0','status':status,'duration_seconds':round(time.monotonic()-t0,3),'steps':results}
(R/'reports/QUICK_AUTHORING_PREFLIGHT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2)); raise SystemExit(0 if status=='PASS' else 1)
