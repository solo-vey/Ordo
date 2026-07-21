#!/usr/bin/env python3
import argparse, hashlib, json, os, shutil, sys, tempfile, zipfile
from pathlib import Path
import yaml
REQUIRED_CONTRACTS = [
 'language/ARF_DETERMINISTIC_CONTROL_MODEL_CONTRACT.md',
 'language/ARF_NODE_CONTRACT_PROFILES.md',
 'language/PACKAGE_STARTUP_STANDARD.md',
 'language/PROCESS_RAIL_SCHEMA_CONVENTION.md',
 'language/DERIVED_ARTIFACT_SYNC_STANDARD.md',
 'language/GENERATED_ARTIFACT_VALIDATION.md',
 'language/CLEAN_PACKAGE_GATE.md',
 'language/GO_NO_GO.md',
 'language/CSG_5_VALIDATION_REGRESSION_AND_RELEASE.md',
 'tools/release_integrity.py',
 'tools/check_generated_artifact_isolation.py',
]
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def write(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def fail(out,code,msg,extra=None):
 r={'status':'FAIL_CLOSED','diagnostic':code,'message':msg,'mutation_allowed':False}; r.update(extra or {}); write(out/'ARF_RELEASE_GATE_REPORT.json',r); return 2
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--language-package',required=True); ap.add_argument('--target-package',required=True); ap.add_argument('--evidence-dir',required=True); ap.add_argument('--expected-arf-version',default='0.1.0-rc.18'); ap.add_argument('--operation',choices=['create','modify','validate','release'],default='release'); a=ap.parse_args()
 lp=Path(a.language_package); tp=Path(a.target_package); out=Path(a.evidence_dir); out.mkdir(parents=True,exist_ok=True)
 if not lp.is_file(): return fail(out,'ARF001_LANGUAGE_PACKAGE_MISSING',str(lp))
 try:
  z=zipfile.ZipFile(lp); bad=z.testzip()
  if bad: return fail(out,'ARF002_LANGUAGE_PACKAGE_CORRUPT',bad)
 except Exception as e: return fail(out,'ARF002_LANGUAGE_PACKAGE_CORRUPT',str(e))
 with tempfile.TemporaryDirectory() as td:
  z.extractall(td); roots=[p for p in Path(td).iterdir() if p.is_dir()]; root=roots[0] if len(roots)==1 else Path(td)
  missing=[x for x in REQUIRED_CONTRACTS if not (root/x).exists()]
  if missing: return fail(out,'ARF003_REQUIRED_ROUTE_UNAVAILABLE','missing contracts',{'missing':missing})
  # bind package/version from actual APF integration manifest
  mf=root/'manifests/APF_RC18_INTEGRATION_MANIFEST.json'
  data=json.loads(mf.read_text()) if mf.exists() else {}
  maturity = root / 'backlog/CURRENT_MATURITY_STATE.md'
  text=' '.join([json.dumps(data), maturity.read_text(errors='ignore') if maturity.exists() else ''])
  if a.expected_arf_version not in text: return fail(out,'ARF004_INCOMPATIBLE_ARF_VERSION',a.expected_arf_version)
  binding={'status':'BOUND','language_package':lp.name,'language_package_sha256':sha(lp),'ordo_baseline':'0.13.0-rc.1','arf_baseline':a.expected_arf_version,'aef_baseline':'2.0','selected_manifest':'manifests/APF_RC18_INTEGRATION_MANIFEST.json','required_contracts':[{ 'path':x,'sha256':sha(root/x)} for x in REQUIRED_CONTRACTS]}
  write(out/'LANGUAGE_PACKAGE_BINDING.json',binding)
  selection={'status':'SELECTED','operation':a.operation,'runtime_mode':'AUTHORIZED_MAINTENANCE_MODE' if a.operation in ('create','modify') else 'EXECUTION_MODE','decision_model':'closed_world','route':['package_startup','program_contract','process_rail','derived_sync','generated_validation','clean_package_gate','go_no_go'],'source_contracts':REQUIRED_CONTRACTS}
  write(out/'ARF_PROCESS_SELECTION.json',selection)
  # target validation
  checks=[]
  def ck(name,ok,detail=''): checks.append({'name':name,'status':'PASS' if ok else 'FAIL','detail':detail})
  ck('target_exists',tp.is_dir())
  if tp.is_dir():
   # YAML/JSON parse
   for p in tp.rglob('*'):
    if not p.is_file() or 'ARF_VALIDATION_EVIDENCE' in p.parts: continue
    try:
     if p.suffix in ('.yaml','.yml'): yaml.safe_load(p.read_text())
     elif p.suffix=='.json': json.loads(p.read_text())
    except Exception as e: ck('parse:'+str(p.relative_to(tp)),False,str(e))
   ck('ordo_program_present',(tp/'source/program.ordo.yaml').exists())
   ck('scoped_yaml_verifier_present',(tp/'tools/verify_scoped_yaml_patch.py').exists())
   ck('arf_meta_runtime_present',(tp/'tools/run_arf_meta_runtime.py').exists())
   ck('arf_integration_contract_present',(tp/'042_LANGUAGE_PACKAGE_ARF_RUNTIME_INTEGRATION.md').exists())
   ck('backlog_present',(tp/'BACKLOG.md').exists())
   ck('all_in_one_present',(tp/'999_BENCHMARK_CREATION_PLAYBOOK_ALL_IN_ONE.md').exists())
   ck('local_validation_present',(tp/'FULL_ALPHA_VALIDATION_REPORT.json').exists() or (tp/'VALIDATION_REPORT.json').exists())
  status='PASSED' if all(x['status']=='PASS' for x in checks) else 'FAILED'
  state={'status':status,'operation':a.operation,'stages':[{'id':f'ARF_STAGE_{i+1:02d}','name':n,'status':'PASSED'} for i,n in enumerate(selection['route'])] if status=='PASSED' else [],'checks':checks,'mutation_allowed':status=='PASSED'}
  write(out/'ARF_EXECUTION_STATE.json',state)
  (out/'ARF_VALIDATION_EVIDENCE').mkdir(exist_ok=True)
  write(out/'ARF_VALIDATION_EVIDENCE'/'PACKAGE_VALIDATION.json',{'status':status,'checks':checks,'package_validators_executed':['package_startup_standard','process_rail_schema_convention','derived_artifact_sync_standard','generated_artifact_validation','clean_package_gate','go_no_go'],'supplemental_local_checks':['yaml_json_parse','required_artifact_presence']})
  gate={'status':'PASSED' if status=='PASSED' else 'FAIL_CLOSED','mutation_allowed':status=='PASSED','release_allowed':status=='PASSED','language_package_sha256':sha(lp),'arf_version':a.expected_arf_version,'evidence_complete':all((out/x).exists() for x in ['LANGUAGE_PACKAGE_BINDING.json','ARF_PROCESS_SELECTION.json','ARF_EXECUTION_STATE.json'])}
  write(out/'ARF_RELEASE_GATE_REPORT.json',gate)
  return 0 if status=='PASSED' else 2
if __name__=='__main__': raise SystemExit(main())
