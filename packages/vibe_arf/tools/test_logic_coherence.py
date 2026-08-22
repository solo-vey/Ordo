#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess,sys,yaml
R=Path(__file__).resolve().parents[1]
checks=[]
def check(name, ok, detail=''):
    checks.append((name,bool(ok),detail))

laws=(R/'PLAYBOOK_LAWS.md').read_text()
# unique machine IDs
law_ids=re.findall(r'\*\*((?:E\d+|P\d+)_[A-Z0-9_]+)\*\*', laws)
check('LAW_IDS_UNIQUE', len(law_ids)==len(set(law_ids)), str([x for x in sorted(set(law_ids)) if law_ids.count(x)>1]))
# self-hosted law projection must contain the full canonical governing set.
prog=yaml.safe_load(open(R/'source/program.ordo.yaml'))
program_laws=[]
def _walk(x):
    if isinstance(x,dict):
        if 'laws' in x and isinstance(x['laws'],list) and x['laws'] and isinstance(x['laws'][0],dict) and 'id' in x['laws'][0]:
            program_laws.extend([i['id'] for i in x['laws']])
        for v in x.values(): _walk(v)
    elif isinstance(x,list):
        for v in x: _walk(v)
_walk(prog)
check('SELF_HOSTED_LAWS_COMPLETE', set(program_laws)==set(law_ids), 'missing='+str(sorted(set(law_ids)-set(program_laws)))+' extra='+str(sorted(set(program_laws)-set(law_ids))))

# E3/E52 lifecycle coherence
m3=re.search(r'\*\*E3_MANDATORY_REGRESSION\*\*[^\n]*',laws)
check('E3_FAST_FULL_COHERENT', bool(m3 and 'applicable lifecycle verification profile' in m3.group(0) and 'FULL' in m3.group(0)), m3.group(0) if m3 else 'missing')
# E33/E36 provenance coherence
m33=re.search(r'\*\*E33_RESULT_SCORE_REQUIRES_PROVEN_MODEL_RESPONSES\*\*[^\n]*',laws)
check('E33_ACCEPTANCE_ONLY_PROVENANCE', bool(m33 and 'acceptance' in m33.group(0).lower() and 'development_score' in m33.group(0)), m33.group(0) if m33 else 'missing')

q=json.load(open(R/'source/quality_acceptance_policy.json'))
rv=q['result_score']['reference_variants']
check('MULTI_REFERENCE_NO_MAX_VARIANT', rv.get('selection')!='maximum_score_across_all_eligible_reference_variants', json.dumps(rv))
check('MULTI_REFERENCE_RELEVANCE_AGGREGATION', 'relevance' in json.dumps(rv).lower() and 'conflict' in json.dumps(rv).lower(), json.dumps(rv))
check('HYBRID_FORMULA_NOT_MECHANICAL_ONLY', 'analytical' in q['result_score'].get('per_document_formula','').lower(), q['result_score'].get('per_document_formula',''))
check('REFERENCE_FIDELITY_HYBRID_NOT_DETERMINISTIC_ONLY', 'hybrid' in q.get('reference_artifact_fidelity',{}).get('scoring','').lower(), q.get('reference_artifact_fidelity',{}).get('scoring',''))

# Gate must prove conflict handling resolution, not merely non-null list.
mod=yaml.safe_load(open(R/'source/modules/60_validation_outputs.ordo.module.yaml'))
gates={g['id']:g for g in mod.get('gates',[])}
g=gates.get('G_AI_REFERENCE_CONFLICTS_RESOLVED',{})
cond=str(g.get('condition',''))
check('REFERENCE_CONFLICT_GATE_FAIL_CLOSED', 'reference_conflict_resolution_status' in cond and 'PASS' in cond,cond)

# Persisted update_state fields in the new evaluator/provenance contour must be schema-declared.
schema=set(prog['state']['schema'])
required_state_fields={
 'improvement_dynamic_eval_plan','improvement_eval_profile','improvement_fresh_comparative_result','improvement_fresh_defects',
 'improvement_model_call_evidence','improvement_reference_conflicts','improvement_reference_profile',
 'improvement_response_provenance_report','improvement_response_provenance_status','improvement_result_scoring_eligible',
 'improvement_sanitized_comparative_defects','improvement_selected_references','improvement_reference_conflict_resolution_status'
}
check('EVALUATOR_STATE_SCHEMA_COMPLETE', required_state_fields <= schema, 'missing='+str(sorted(required_state_fields-schema)))
check('NO_STATE_FIELDS_OUTSIDE_SCHEMA', not [k for k in prog['state'] if k not in ('id','schema')], str([k for k in prog['state'] if k not in ('id','schema')]))

# Every accumulated working workstream must have mandatory verification-profile coverage.
ext=json.load(open(R/'verification/PROFILE_EXTENSIONS.json'))
profile_checks={c.get('id') for c in ext.get('checks',[]) if c.get('required') is True}
required_feature_checks={
 'scoring_v3_development_acceptance','constructive_correctness','data_layer_first_hard_architecture',
 'reusable_authoring_templates','hybrid_reference_fidelity_feedback','deterministic_first_execution',
 'information_preservation_monotonic_evidence','dynamic_multi_reference_comparative_evaluator',
 'editor_visible_architecture','fast_full_dependency_aware_validation','default_debug_handoff_progress','generated_playbook_production_package_contract','logic_coherence',
 'alpha44_distribution_package_validator','alpha44_authoring_execution_watchdog','alpha44_generated_playbook_semantic_execution'
}
check('WORKSTREAM_PROFILE_COVERAGE_COMPLETE', required_feature_checks <= profile_checks, 'missing='+str(sorted(required_feature_checks-profile_checks)))

# Responsibility map complete and semantic classification sensible.
p=subprocess.run([sys.executable,str(R/'tools/verify_execution_responsibility_map.py'),str(R)],capture_output=True,text=True)
try: resp=json.loads(p.stdout)
except Exception: resp={}
check('EXECUTION_RESPONSIBILITY_MAP_COMPLETE', resp.get('status')=='PASS', json.dumps(resp.get('findings',[])))
mp=json.load(open(R/'verification/EXECUTION_RESPONSIBILITY_MAP.json'))
entries={e['element_id']:e for e in mp['entries']}
expected={
 'N_AI_DISCOVER_ARTIFACT_EVAL_PROFILE':'model_judgment',
 'N_AI_SELECT_GOLDEN_REFERENCES':'model_judgment',
 'N_AI_BUILD_REFERENCE_PROFILE':'model_judgment',
 'N_AI_BUILD_DYNAMIC_COMPARATIVE_PROMPT':'deterministic',
 'N_AI_RUN_FRESH_COMPARATIVE_EVALUATOR':'model_judgment',
 'N_AI_SANITIZE_EVALUATION_DEFECTS':'deterministic',
 'G_AI_REFERENCE_CONFLICTS_RESOLVED':'deterministic',
 'G_AI_FRESH_REFERENCE_FIDELITY':'deterministic',
}
for eid,cls in expected.items():
 check('RESP_'+eid, entries.get(eid,{}).get('class')==cls, str(entries.get(eid)))

failed=[x for x in checks if not x[1]]
for n,ok,d in checks: print(('PASS' if ok else 'FAIL'),n,(':: '+d if d and not ok else ''))
print(f'LOGIC_COHERENCE: {len(checks)-len(failed)}/{len(checks)} PASS')
sys.exit(1 if failed else 0)
