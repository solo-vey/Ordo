#!/usr/bin/env python3
from pathlib import Path
import io,json,subprocess,sys,tempfile,zipfile,hashlib
R=Path(__file__).resolve().parents[1]; T=R/'tools/validate_distribution_package.py'; checks=[]
def ck(n,v): checks.append((n,bool(v)))
def nested():
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        for n in ['MODEL_BUNDLE.yaml','variable_catalog.yaml','variable_group_catalog.yaml','information_dependency_graph.yaml','artifact_catalog.yaml','playbook_projection.yaml']: z.writestr(n,'x: 1\n')
    return b.getvalue()
def contract():
    return {'profiles':{
      'CLI_RUN':{'forbidden_prefixes':['reports/','runtime/','evaluator/','authoring/'],'forbidden_name_tokens':['golden'],'start_files':['START_HERE_CLI_RUN.md','START_PROMPT_CLI_RUN.md']},
      'MODEL_RUN':{'forbidden_prefixes':['reports/','runtime/','evaluator/','authoring/','compiled/','cli_embedded/','tests/'],'forbidden_name_tokens':['golden'],'start_files':['START_HERE_MODEL_MODE.md','START_PROMPT_MODEL_MODE.md']}}}
def continuity(profile,src='same'):
    return {'profile':profile,'version':'0.test','canonical_source_identity':src,'source_identity_files':[], 'dependency_closure_sha256':None,'member_set_sha256':'x','startup_files':[], 'rebuild_recipe':{},'packaging_policy_sha256':'x','validator_applicability_policy_sha256':'x'}
def make(path,profile='EDIT',bad_surface=False,run_extra=False,src='same'):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('DISTRIBUTION_MANIFEST.json',json.dumps({'distribution':profile,'source_identity_sha256':src,'version':'0.test'}))
        z.writestr('PACKAGE_CONTINUITY_MANIFEST.json',json.dumps(continuity(profile,src)))
        z.writestr('DISTRIBUTION_PACKAGE_CONTRACT.json',json.dumps(contract()))
        if profile=='EDIT':
            base='applied_dataflow/' if bad_surface else 'design/'
            for n in ['MODEL_BUNDLE.yaml','variable_catalog.yaml','variable_group_catalog.yaml','information_dependency_graph.yaml','artifact_catalog.yaml','playbook_projection.yaml']: z.writestr(base+n,'x: 1\n')
            if not bad_surface: z.writestr('design/DATA_FLOW_PACKAGE.zip',nested())
        else:
            starts=contract()['profiles'][profile]['start_files']
            for s in starts: z.writestr(s,'start\n')
            z.writestr(profile+'_PACKAGE_DEPENDENCY_CLOSURE.json','{}')
            z.writestr('analyst_context/context_catalog.json','{}')
            if run_extra: z.writestr('authoring/old.yaml','x: 1\n')
def run(args):
    p=subprocess.run([sys.executable,str(T),*args],capture_output=True,text=True,timeout=10); return p.returncode,json.loads(p.stdout)
with tempfile.TemporaryDirectory() as td:
    td=Path(td); edit=td/'e.zip'; cli=td/'c.zip'; model=td/'m.zip'; bad=td/'bad.zip'; badc=td/'badc.zip'
    make(edit,'EDIT'); make(cli,'CLI_RUN'); make(model,'MODEL_RUN'); make(bad,'EDIT',bad_surface=True); make(badc,'CLI_RUN',run_extra=True)
    rc,d=run([str(edit),'--mode','dev']); ck('DEV_ALIAS_PASS',rc==0 and d['status']=='PASS')
    rc,d=run([str(edit),'--mode','debug']); ck('DEBUG_ALIAS_PASS',rc==0)
    rc,d=run([str(cli),'--mode','run']); ck('RUN_ALIAS_PASS',rc==0)
    rc,d=run(['--mode','pair','--dev',str(edit),'--run',str(cli),'--model-run',str(model)]); ck('PAIR_ALIAS_PASS',rc==0)
    rc,d=run([str(bad),'--mode','edit']); ck('EDIT_DATAFLOW_BLOCKED',rc!=0 and any(x['code']=='EDIT_EDITOR_DATAFLOW_SURFACE_MISSING' for x in d['findings']))
    rc,d=run([str(badc),'--mode','cli_run']); ck('AUTHORING_BAGGAGE_BLOCKED',rc!=0 and any(x['code']=='CLI_RUN_FORBIDDEN_BAGGAGE' for x in d['findings']))
    make(model,'MODEL_RUN',src='other'); rc,d=run(['--mode','release','--edit',str(edit),'--cli-run',str(cli),'--model-run',str(model)]); ck('SOURCE_PARITY_BLOCKED',rc!=0 and any(x['code']=='RELEASE_SOURCE_PARITY' for x in d['findings']))
    ck('POLICY_PRESENT',(R/'source/distribution-package-validation-policy.json').is_file())
failed=[n for n,v in checks if not v]
for n,v in checks: print(('PASS' if v else 'FAIL'),n)
print(f'ALPHA44_DISTRIBUTION_PACKAGE_VALIDATOR: {len(checks)-len(failed)}/{len(checks)} PASS')
raise SystemExit(1 if failed else 0)
