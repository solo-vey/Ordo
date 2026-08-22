#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
RESULTS=[]
def check(name,cond,detail=''):
    RESULTS.append({'name':name,'status':'PASS' if cond else 'FAIL','detail':detail})
def run(*args):
    return subprocess.run([sys.executable,*map(str,args)],capture_output=True,text=True,timeout=60)
def yload(p):
    p=ROOT/p
    return yaml.safe_load(p.read_text(encoding='utf-8')) if p.is_file() else None
def jload(p):
    p=ROOT/p
    return json.loads(p.read_text(encoding='utf-8')) if p.is_file() else None

authoring_files=[
 'authoring/information_object_catalog.yaml','authoring/information_group_catalog.yaml',
 'authoring/artifact_catalog.yaml','authoring/information_flow_graph.yaml',
 'authoring/interaction_projection.yaml','authoring/ordo_projection.yaml']
check('A25_SELF_AIM_PACKAGE_EXISTS',all((ROOT/p).is_file() for p in authoring_files),','.join(p for p in authoring_files if not (ROOT/p).is_file()))

policy=jload('source/vibe-self-hosting-policy.json')
check('A25_SELF_HOSTING_POLICY',bool(policy and policy.get('same_authoring_contract_as_generated_playbooks') is True and policy.get('special_authoring_path_for_vibe') is False))

oc=yload('authoring/information_object_catalog.yaml') or {}
check('A25_SELF_MODEL_ID',oc.get('model_id')=='VIBE_ARF_SELF_INFORMATION_MODEL')

validator=ROOT/'tools/validate_authoring_information_model.py'
if validator.is_file():
    r=run(validator,ROOT)
    check('A25_SELF_AIM_VALIDATES',r.returncode==0,(r.stdout+r.stderr)[-1200:])
else: check('A25_SELF_AIM_VALIDATES',False,'validator missing')

proj=ROOT/'tools/validate_information_projection.py'
if proj.is_file():
    r=run(proj,ROOT,'--playbook',ROOT/'source','--require-bound')
    check('A25_SELF_PROJECTION_VALIDATES_MODULAR_SOURCE',r.returncode==0,(r.stdout+r.stderr)[-1600:])
else: check('A25_SELF_PROJECTION_VALIDATES_MODULAR_SOURCE',False,'projection validator missing')

# actual executable surface
actual_nodes=[]
arch=yload('source/modules/30_vibe_architecture.ordo.module.yaml') or {}
actual_nodes=[str(x.get('id')) for x in (arch.get('nodes') or []) if isinstance(x,dict) and x.get('id')]
out=yload('source/modules/60_validation_outputs.ordo.module.yaml') or {}
actual_gates=[str(x.get('id')) for x in (out.get('gates') or []) if isinstance(x,dict) and x.get('id')]
pr=yload('authoring/ordo_projection.yaml') or {}
managed=set(((pr.get('playbook') or {}).get('managed_node_scope') or []))
check('A25_ALL_VIBE_NODES_MANAGED',set(actual_nodes).issubset(managed),str(sorted(set(actual_nodes)-managed)[:20]))
check('A25_ALL_VIBE_GATES_MANAGED',set(actual_gates).issubset(managed),str(sorted(set(actual_gates)-managed)[:20]))
allrefs=set()
for k in ['information_bindings','group_bindings','gate_bindings','artifact_bindings']:
    for b in pr.get(k) or []:
        allrefs.update(str(x) for x in (b.get('node_ids') or []))
check('A25_REVERSE_MAPPING_COVERS_MANAGED',managed.issubset(allrefs),str(sorted(managed-allrefs)[:20]))

fg=yload('authoring/information_flow_graph.yaml') or {}
node_by={str(x.get('id')):x for x in (fg.get('nodes') or []) if isinstance(x,dict) and x.get('id')}
arts=yload('authoring/artifact_catalog.yaml') or {}
art_ids={str(x.get('id')) for x in arts.get('artifacts') or [] if isinstance(x,dict) and x.get('id')}
check('A25_SELF_FLOW_HAS_TERMINAL_DELIVERY_ARTIFACT',bool(art_ids and art_ids.intersection(set(fg.get('terminal_nodes') or []))))
check('A25_SELF_FLOW_HAS_VALIDATION_AND_AUTHORITY',any(x.get('kind')=='validation_gate' for x in node_by.values()) and any(x.get('kind')=='authority_decision' for x in node_by.values()))
edge_types={str(x.get('type')) for x in (fg.get('edges') or []) if isinstance(x,dict)}
check('A25_SELF_FLOW_TYPED_RELATIONSHIPS',{'provided_by','derived_from','validated_by','materializes','depends_on'}.issubset(edge_types),str(sorted(edge_types)))

ip=yload('authoring/interaction_projection.yaml') or {}
ipol=ip.get('policy') or {}
check('A25_SELF_INTERACTION_PROGRESSIVE',ipol.get('progressive_intake') is True and ipol.get('proposal_first_when_derivable') is True and ipol.get('human_only_for_authority_or_unresolved_semantics') is True)

laws=(ROOT/'PLAYBOOK_LAWS.md').read_text(encoding='utf-8') if (ROOT/'PLAYBOOK_LAWS.md').is_file() else ''
source_laws=yload('source/modules/40_policies.ordo.module.yaml') or {}
source_law_ids={str(x.get('id')) for x in ((source_laws.get('playbook_laws') or {}).get('laws') or []) if isinstance(x,dict)}
check('A25_SELF_HOSTING_LAW_PROPAGATED','E14_SELF_HOSTED_INFORMATION_MODEL' in laws and 'E14_SELF_HOSTED_INFORMATION_MODEL' in source_law_ids)

vp=jload('verification_profile.json') or {}
checks={c.get('id'):c for c in vp.get('checks') or [] if isinstance(c,dict)}
self_checks={'vibe_self_authoring_information_model','vibe_self_information_projection'}
check('A25_SELF_GATES_IN_PRE_EDITOR',self_checks.issubset(checks) and all(checks[x].get('required') is True and checks[x].get('phase')=='PRE_EDITOR' for x in self_checks if x in checks),str(sorted(self_checks-set(checks))))

ext=jload('verification/PROFILE_EXTENSIONS.json') or {}
extids={c.get('id') for c in ext.get('checks') or [] if isinstance(c,dict)}
check('A25_REGRESSION_REGISTERED','alpha25_self_hosted_information_model' in extids)

# self AIM is generic to Vibe behavior, not tied to prior domain experiment.
blob='\n'.join((ROOT/p).read_text(encoding='utf-8') for p in authoring_files if (ROOT/p).is_file()).lower()
forbidden=['risk_factor_passport','risk factor passport','severity_level','risk_owner']
check('A25_SELF_AIM_DOMAIN_NEUTRAL',not any(x in blob for x in forbidden),str([x for x in forbidden if x in blob]))

passed=sum(x['status']=='PASS' for x in RESULTS); failed=len(RESULTS)-passed
report={'schema_version':'1.0','suite':'alpha25_self_hosted_information_model','passed':passed,'failed':failed,'tests':RESULTS}
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if failed==0 else 1)
