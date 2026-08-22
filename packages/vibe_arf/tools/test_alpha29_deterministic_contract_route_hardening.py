#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
RES=[]
def check(name,cond,detail=''):
    RES.append({'name':name,'status':'PASS' if cond else 'FAIL','detail':str(detail)})
def run(script,pkg,*extra):
    p=ROOT/'tools'/script
    if not p.is_file(): return None
    return subprocess.run([sys.executable,str(p),str(pkg),*map(str,extra)],capture_output=True,text=True)
def write_pkg(root:Path, *, route='END_DONE', archive=True, registry_mode='good', tool_ref=True, writes=True):
    (root/'source').mkdir(parents=True,exist_ok=True); (root/'verification').mkdir(exist_ok=True); (root/'tools').mkdir(exist_ok=True)
    prod={
      'id':'N_BUILD','type':'automatic','action':'PACKAGE.MATERIALIZE',
      'execution_contract':{'owner':'deterministic','advancement':'automatic','runtime_executor':'package_tool'},
      'next':'G_VALID','artifact':{'state_path':'artifact_ref','expected_path':'generated/out.zip' if archive else 'generated/out.md'},
      'output':'generated/out.zip' if archive else 'generated/out.md'
    }
    if tool_ref: prod['tool_ref']='tools/build.py'
    if writes: prod['writes']=['artifact_ref']
    else:
        prod.pop('output',None); prod.pop('artifact',None)
    program={
      'playbook':{'id':'regression.fixture','version':'0.1.0'},
      'graph_contract':{'entry_node':'N_BUILD','external_terminal_targets':['END_DONE']},
      'state':{'schema':{'artifact_ref':None}},
      'nodes':[prod],
      'gates':[{'id':'G_VALID','method':'mechanical','trust_class':'deterministic','condition':'artifact/archive validation is PASS','allowed_from':['N_BUILD'],'on_pass':'END_DONE','on_fail':route}],
      'outputs':[{'id':'OUT_ARCH','type':'archive' if archive else 'document','allowed_after':['G_VALID']}]
    }
    (root/'source/program.ordo.yaml').write_text(yaml.safe_dump(program,sort_keys=False),encoding='utf-8')
    (root/'tools/build.py').write_text('print("ok")\n',encoding='utf-8')
    if registry_mode!='missing':
      content={'source':'canonical approved state','no_stale_required_variables':True}
      if archive and registry_mode!='missing_members': content['required_members']=['payload.txt']
      if archive: content['forbidden_members']=[]
      if archive and registry_mode!='missing_hash': content['member_hashes']={'payload.txt':'0'*64}
      validators=[] if registry_mode=='missing_validator' else ['tools/validate.py']
      reg={'schema_version':'1.0','artifacts':[{
        'artifact_id':'OUT_ARCH','output_type':'archive' if archive else 'document','output_path':prod.get('output','generated/out.md'),
        'materialization_mode':'assembler','assembler_ref':'tools/build.py','materialization_node_id':'N_BUILD',
        'validators':validators,'post_materialization_validation_required':True,'content_contract':content,'version':'1'
      }]}
      (root/'verification/ARTIFACT_MATERIALIZATION_REGISTRY.json').write_text(json.dumps(reg,indent=2),encoding='utf-8')
      (root/'tools/validate.py').write_text('print("ok")\n',encoding='utf-8')
    return root

check('A29_DETERMINISTIC_VALIDATOR_EXISTS',(ROOT/'tools/validate_deterministic_contract_completeness.py').is_file())
check('A29_ARTIFACT_REGISTRY_VALIDATOR_EXISTS',(ROOT/'tools/validate_artifact_archive_registry_completeness.py').is_file())

with tempfile.TemporaryDirectory() as td:
    b=write_pkg(Path(td)/'bad_route',route='block')
    r=run('verify_generated_playbook_contract.py',b,'--target','language_core')
    detail=(r.stdout+r.stderr) if r else 'validator missing'
    check('A29_UNDECLARED_BLOCK_ROUTE_REJECTED',r is not None and r.returncode!=0 and 'GP_GRAPH_UNKNOWN_TARGET' in detail,detail[-1500:])
with tempfile.TemporaryDirectory() as td:
    b=write_pkg(Path(td)/'reserved_stop',route='STOP')
    r=run('verify_generated_playbook_contract.py',b,'--target','language_core')
    check('A29_CANONICAL_STOP_ROUTE_ALLOWED',r is not None and r.returncode==0,(r.stdout+r.stderr)[-1500:] if r else 'missing')

cases=[
 ('A29_ARCHIVE_REGISTRY_REQUIRED','missing'),
 ('A29_ARCHIVE_MEMBERS_REQUIRED','missing_members'),
 ('A29_ARCHIVE_HASH_REQUIRED','missing_hash'),
 ('A29_POST_VALIDATOR_REQUIRED','missing_validator'),
]
for name,mode in cases:
    with tempfile.TemporaryDirectory() as td:
        b=write_pkg(Path(td)/mode,registry_mode=mode)
        r=run('validate_artifact_archive_registry_completeness.py',b)
        check(name,r is not None and r.returncode!=0,(r.stdout+r.stderr)[-1500:] if r else 'missing validator')
with tempfile.TemporaryDirectory() as td:
    b=write_pkg(Path(td)/'good_archive')
    r=run('validate_artifact_archive_registry_completeness.py',b)
    check('A29_COMPLETE_ARCHIVE_PROFILE_PASSES',r is not None and r.returncode==0,(r.stdout+r.stderr)[-1500:] if r else 'missing validator')

for name,kwargs in [
 ('A29_PACKAGE_TOOL_TOOL_REF_REQUIRED',{'tool_ref':False}),
 ('A29_PACKAGE_TOOL_EFFECT_REQUIRED',{'writes':False}),
]:
    with tempfile.TemporaryDirectory() as td:
        b=write_pkg(Path(td)/name,archive=False,**kwargs)
        r=run('validate_deterministic_contract_completeness.py',b)
        check(name,r is not None and r.returncode!=0,(r.stdout+r.stderr)[-1500:] if r else 'missing validator')
with tempfile.TemporaryDirectory() as td:
    b=write_pkg(Path(td)/'good_det',archive=False)
    r=run('validate_deterministic_contract_completeness.py',b)
    check('A29_COMPLETE_PACKAGE_TOOL_CONTRACT_PASSES',r is not None and r.returncode==0,(r.stdout+r.stderr)[-1500:] if r else 'missing validator')

try: vp=json.loads((ROOT/'verification_profile.json').read_text())
except Exception: vp={}
ids={c.get('id') for c in vp.get('checks',[]) if isinstance(c,dict)}
check('A29_PROFILE_WIRES_DETERMINISTIC_COMPLETENESS','deterministic_contract_completeness' in ids,sorted(ids))
check('A29_PROFILE_WIRES_ARTIFACT_REGISTRY_COMPLETENESS','artifact_archive_registry_completeness' in ids,sorted(ids))
try: pol=json.loads((ROOT/'source/generated-playbook-regression-policy.json').read_text())
except Exception: pol={}
a29=set(pol.get('alpha29_contracts') or [])
check('A29_POLICY_DECLARED',{'strict_route_closure','deterministic_contract_completeness','artifact_archive_registry_completeness'}.issubset(a29),sorted(a29))
try: inv=json.loads((ROOT/'verification/INVARIANT_REGISTER.json').read_text())
except Exception: inv={}
iids={x.get('id') for x in inv.get('invariants',[]) if isinstance(x,dict)}
check('A29_INVARIANTS_REGISTERED',{'STRICT_ROUTE_CLOSURE','DETERMINISTIC_CONTRACT_COMPLETE','ARTIFACT_ARCHIVE_REGISTRY_COMPLETE'}.issubset(iids),sorted(iids))
mat=(ROOT/'tools/materialize_generated_playbook_verification.py').read_text(encoding='utf-8',errors='ignore') if (ROOT/'tools/materialize_generated_playbook_verification.py').is_file() else ''
check('A29_GENERATED_INHERITANCE_WIRED','validate_deterministic_contract_completeness.py' in mat and 'validate_artifact_archive_registry_completeness.py' in mat,'materializer missing new validators')
check('A29_MATERIALIZER_PRESERVES_STRUCTURED_REGISTRY','existing_registry' in mat and 'Do not overwrite structured artifact/archive' in mat,'late materializer may overwrite authored registry')

passed=sum(x['status']=='PASS' for x in RES); failed=len(RES)-passed
print(json.dumps({'schema_version':'1.0','suite':'alpha29_deterministic_contract_route_hardening','passed':passed,'failed':failed,'tests':RES},ensure_ascii=False,indent=2))
raise SystemExit(0 if failed==0 else 1)
