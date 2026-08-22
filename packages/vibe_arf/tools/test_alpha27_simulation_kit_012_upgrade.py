#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RES=[]
def check(name,cond,detail=''):
    RES.append({'name':name,'status':'PASS' if cond else 'FAIL','detail':detail})
def j(rel):
    p=ROOT/rel
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception:return None

dep=j('verification/SIMULATION_KIT_DEPENDENCY.json') or {}

def ver(v):
    try:return tuple(int(x) for x in str(v).split('.'))
    except:return (0,)
check('A27_SIMKIT_VERSION_AT_LEAST_012',ver(dep.get('version')) >= ver('0.1.2'),str(dep.get('version')))
check('A27_SIMKIT_RUNTIME_AT_LEAST_0163', any(f'0.2.0-alpha.20.0.{n}-dev' in str(dep.get('runtime_baseline','')) for n in range(163,1000)), str(dep.get('runtime_baseline')))
check('A27_SIMKIT_PATH_CURRENT', str(dep.get('path','')).endswith(f'ORDO_PLAYBOOK_SIMULATION_KIT_{dep.get("version")}.zip'), str(dep.get('path')))
kit=ROOT/str(dep.get('path','')) if dep.get('path') else Path('/nonexistent')
check('A27_SIMKIT_DEP_EXISTS',kit.is_file(),str(kit))
if kit.is_file():
    got=hashlib.sha256(kit.read_bytes()).hexdigest()
    check('A27_SIMKIT_HASH_PINNED',got==dep.get('sha256'),got)
else: check('A27_SIMKIT_HASH_PINNED',False,'missing')

wrapper=(ROOT/'tools/run_simulation_preflight.py').read_text(encoding='utf-8',errors='ignore') if (ROOT/'tools/run_simulation_preflight.py').is_file() else ''
check('A27_WRAPPER_SUPPORTS_FLAT_ROOT','ordo_simulate.py' in wrapper and ('kit_root' in wrapper or 'resolve_kit_root' in wrapper), 'flat-root resolver missing')
check('A27_WRAPPER_USES_NATIVE_RECOVERY_POINTS','semantic_recovery_fixture_points' in wrapper,'native recovery points absent')
check('A27_WRAPPER_PRESERVES_MISSING_FIXTURES','missing_fixtures.json' in wrapper and 'missing_model_responses.template.yaml' in wrapper,'missing-fixture evidence not preserved')
check('A27_WRAPPER_CLASSIFIES_FIXTURE_INCOMPLETE','SIMULATION_FIXTURE_INCOMPLETE' in wrapper,'fixture_incomplete classification absent')

pol=j('source/simulation-first-verification-policy.json') or {}
wf=set(pol.get('required_workflow') or [])
check('A27_POLICY_DYNAMIC_RECOVERY_DISCOVERY','resolve_dynamic_missing_fixtures' in wf or 'iterate_fixture_incomplete_until_closed' in wf,str(sorted(wf)))
check('A27_POLICY_PROFILE_ADAPTER_BOUNDARY',pol.get('profile_adapter_rule')=='explicit_adapter_not_language_semantics',str(pol.get('profile_adapter_rule')))

# Heavy dependency self-check/smoke is a separate PRE_EDITOR python gate, not nested inside trusted regression.
check('A27_DEPENDENCY_GATE_EXISTS',(ROOT/'tools/verify_simulation_kit_dependency.py').is_file())
vp=j('verification_profile.json') or {}
check('A27_DEPENDENCY_GATE_WIRED',any(c.get('id')=='simulation_kit_dependency_integrity' for c in (vp.get('checks') or [])),'simulation_kit_dependency_integrity missing')

passed=sum(x['status']=='PASS' for x in RES); failed=len(RES)-passed
print(json.dumps({'schema_version':'1.0','suite':'alpha27_simulation_kit_012_upgrade','passed':passed,'failed':failed,'tests':RES},ensure_ascii=False,indent=2))
raise SystemExit(0 if failed==0 else 1)
