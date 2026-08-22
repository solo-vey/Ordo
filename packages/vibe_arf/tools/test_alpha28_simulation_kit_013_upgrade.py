#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
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
check('A28_SIMKIT_VERSION_AT_LEAST_013', ver(dep.get('version')) >= ver('0.1.3'), str(dep.get('version')))
check('A28_SIMKIT_RUNTIME_AT_LEAST_0164', any(f'0.2.0-alpha.20.0.{n}-dev' in str(dep.get('runtime_baseline','')) for n in range(164,1000)), str(dep.get('runtime_baseline')))
check('A28_SIMKIT_PATH_CURRENT', str(dep.get('path','')).endswith(f'ORDO_PLAYBOOK_SIMULATION_KIT_{dep.get("version")}.zip'), str(dep.get('path')))
kit=ROOT/str(dep.get('path','')) if dep.get('path') else Path('/nonexistent')
check('A28_SIMKIT_DEP_EXISTS',kit.is_file(),str(kit))
if kit.is_file():
    got=hashlib.sha256(kit.read_bytes()).hexdigest(); check('A28_SIMKIT_HASH_PINNED',got==dep.get('sha256'),got)
else: check('A28_SIMKIT_HASH_PINNED',False,'missing')
check('A28_ACCEPTANCE_EVIDENCE_DECLARED',bool(dep.get('acceptance_evidence')),str(dep.get('acceptance_evidence')))

wrapper=(ROOT/'tools/run_simulation_preflight.py').read_text(encoding='utf-8',errors='ignore') if (ROOT/'tools/run_simulation_preflight.py').is_file() else ''
check('A28_WRAPPER_PRESERVES_PROFILE_GAPS','profile_contract_gaps.json' in wrapper,'profile contract gap evidence not preserved')
check('A28_WRAPPER_CLASSIFIES_PROFILE_GAP','VIBE_AUTHORING_PROFILE_CONTRACT_GAP' in wrapper,'profile gap ownership classification absent')
check('A28_WRAPPER_NOT_FIXTURE_MISCLASSIFY','profile_contract_gap' in wrapper and 'SIMULATION_FIXTURE_INCOMPLETE' in wrapper,'distinct profile-gap vs fixture logic absent')

pol=j('source/simulation-first-verification-policy.json') or {}
check('A28_POLICY_ARTIFACT_VALIDATION_RULE',bool(pol.get('deterministic_artifact_validation_rule')),str(pol.get('deterministic_artifact_validation_rule')))
check('A28_POLICY_PROFILE_GAP_RULE',bool(pol.get('profile_contract_gap_rule')),str(pol.get('profile_contract_gap_rule')))
check('A28_POLICY_ADAPTER_BOUNDARY',pol.get('profile_adapter_rule')=='explicit_adapter_not_language_semantics',str(pol.get('profile_adapter_rule')))

grp=j('source/generated-playbook-regression-policy.json') or {}
check('A28_REGRESSION_CONTRACTS',all(x in set(grp.get('alpha28_contracts') or []) for x in ['simulation_kit_0.1.3_pin','deterministic_artifact_archive_validation','profile_contract_gap_preservation','profile_contract_gap_defect_ownership']),str(grp.get('alpha28_contracts')))

selfp=j('source/vibe-self-hosting-policy.json') or {}
check('A28_SELF_HOST_CHECK',any('0.1.3' in str(x) for x in (selfp.get('alpha28_self_checks') or [])),str(selfp.get('alpha28_self_checks')))

vp=j('verification_profile.json') or {}
check('A28_REGRESSION_WIRED',any(c.get('id')=='alpha28_simulation_kit_013_upgrade' for c in (vp.get('checks') or [])),'alpha28 check missing')
inv=j('verification/INVARIANT_REGISTER.json') or {}
ids={x.get('id') for x in inv.get('invariants',[]) if isinstance(x,dict)}
check('A28_INVARIANT_REGISTERED','PINNED_SIMULATION_KIT_013_RUNTIME_0164' in ids,'new kit invariant absent')

passed=sum(x['status']=='PASS' for x in RES); failed=len(RES)-passed
print(json.dumps({'schema_version':'1.0','suite':'alpha28_simulation_kit_013_upgrade','passed':passed,'failed':failed,'tests':RES},ensure_ascii=False,indent=2))
raise SystemExit(0 if failed==0 else 1)
