#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, tempfile, zipfile, sys
R=Path(__file__).resolve().parents[1]; checks=[]
def ck(name,cond,detail=''): checks.append((name,bool(cond),detail))
with tempfile.TemporaryDirectory() as td:
 td=Path(td)
 b=subprocess.run(['python',str(R/'tools/build_three_profile_playbook_distribution.py'),str(R),str(td),'--stem','REG'],capture_output=True,text=True)
 ck('three_profile_build_pass',b.returncode==0,b.stdout+b.stderr)
 edit=td/'REG_EDIT.zip'; cli=td/'REG_CLI_RUN.zip'; model=td/'REG_MODEL_RUN.zip'
 for n,p in [('edit_exists',edit),('cli_exists',cli),('model_exists',model)]: ck(n,p.is_file())
 if all(p.is_file() for p in (edit,cli,model)):
  v=subprocess.run(['python',str(R/'tools/validate_distribution_package.py'),'--mode','release','--edit',str(edit),'--cli-run',str(cli),'--model-run',str(model)],capture_output=True,text=True)
  ck('release_validate_pass',v.returncode==0,v.stdout+v.stderr)
  with zipfile.ZipFile(edit) as ez, zipfile.ZipFile(cli) as cz, zipfile.ZipFile(model) as mz:
   en,cn,mn=set(ez.namelist()),set(cz.namelist()),set(mz.namelist())
   ck('edit_preserves_engineering_surfaces',all(any(x.startswith(p) for x in en) for p in ['authoring/','verification/','editor/','patterns/']))
   ck('cli_smaller_than_edit',len(cn)<len(en)); ck('model_smaller_than_edit',len(mn)<len(en))
   ck('model_forbids_authoring',not any(x.startswith(('authoring/','verification/','editor/')) for x in mn))
failed=[n for n,c,d in checks if not c]
print(json.dumps({'status':'PASS' if not failed else 'FAIL','passed':sum(c for _,c,_ in checks),'total':len(checks),'failed':failed,'details':{n:d for n,c,d in checks if not c and d}},indent=2)); sys.exit(0 if not failed else 1)
