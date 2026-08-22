#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=[]
def ck(i,c,d=''): R.append({'id':i,'status':'PASS' if c else 'FAIL','detail':d})
def j(p): return json.loads((ROOT/p).read_text())
dep=j('verification/SIMULATION_KIT_DEPENDENCY.json')
ck('VERSION_016',dep.get('version')=='0.1.6',str(dep.get('version')))
ck('BASELINE_0166','0.2.0-alpha.20.0.166-dev' in dep.get('runtime_baseline',''),dep.get('runtime_baseline',''))
ck('STRICT_DEFAULT',dep.get('gate_contract_mode_default')=='strict',str(dep.get('gate_contract_mode_default')))
ck('SURVIVABILITY_DECLARED',dep.get('state_survivability_evidence')=='state_survivability.json',str(dep.get('state_survivability_evidence')))
z=ROOT/dep['path']; ck('ZIP_EXISTS',z.is_file(),str(z))
actual_hash=hashlib.sha256(z.read_bytes()).hexdigest() if z.is_file() else ''
ck('HASH_PIN',actual_hash==dep.get('sha256'),actual_hash)
acc=ROOT/dep.get('acceptance_evidence','')
ck('ACCEPTANCE_EXISTS',acc.is_file(),str(acc))
if acc.is_file():
 a=json.loads(acc.read_text())
 ck('ACCEPTANCE_PASS',a.get('status')=='PASS' and (a.get('kit_zip_sha256') or a.get('zip_sha256'))==dep.get('sha256'),str(a.get('status')))
 ck('SELF_CHECK_PASS',(a.get('self_check') or {}).get('status')=='PASS',str((a.get('self_check') or {}).get('status')))
 u=a.get('unit_tests') or {}; ck('UNIT_016_PASS',u.get('status')=='PASS' and int(u.get('passed') or 0)>=13 and int(u.get('failed') or 0)==0,str(u))
 tr=((a.get('runtime_smoke') or {}).get('vibe_terminal_run') or {}); ck('TERMINAL_SIMULATION_PASS',tr.get('status')=='PASS' and int(tr.get('errors') or 0)==0 and int(tr.get('steps') or 0)>0,str(tr))
else:
 for x in ['ACCEPTANCE_PASS','SELF_CHECK_PASS','UNIT_016_PASS','TERMINAL_SIMULATION_PASS']: ck(x,False)
if z.is_file():
 with tempfile.TemporaryDirectory() as td:
  td=Path(td); zipfile.ZipFile(z).extractall(td); roots=[p for p in td.iterdir() if p.is_dir()]; root=roots[0] if len(roots)==1 else td
  rel='\n'.join((root/f).read_text(errors='ignore') for f in ['KIT_RELEASE_NOTES_0.1.6.md','KIT_RELEASE_NOTES_0.1.5.md'] if (root/f).is_file())
  ck('STRICT_RELEASE_RULE','gate-contract-mode strict' in rel)
  ck('PRODUCER_GUARANTEE_RULE','GATE_INPUT_PRODUCER_NOT_GUARANTEED' in rel)
  ck('DESTRUCTIVE_OVERWRITE_RULE','REQUIRED_PATH_ANCESTOR_DESTRUCTIVE_OVERWRITE' in rel)
else:
 for x in ['STRICT_RELEASE_RULE','PRODUCER_GUARANTEE_RULE','DESTRUCTIVE_OVERWRITE_RULE']: ck(x,False)
failed=sum(x['status']=='FAIL' for x in R)
print(json.dumps({'suite':'simulation_kit_015_current','status':'PASS' if not failed else 'FAIL','passed':len(R)-failed,'failed':failed,'checks':R},indent=2))
raise SystemExit(1 if failed else 0)
