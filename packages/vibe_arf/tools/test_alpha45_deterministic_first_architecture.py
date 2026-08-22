#!/usr/bin/env python3
from pathlib import Path
import json, yaml
R=Path(__file__).resolve().parents[1]
checks={}
def ck(k,v): checks[k]=bool(v)
def j(rel):
 p=R/rel
 return json.loads(p.read_text(encoding='utf-8')) if p.is_file() else {}
def y(rel):
 p=R/rel
 return yaml.safe_load(p.read_text(encoding='utf-8')) if p.is_file() else {}

policy=j('source/deterministic-first-architecture-policy.json')
inherit=j('source/generated-playbook-execution-inheritance-policy.json')
safe=j('source/generated-playbook-safe-node-profiles.json')
patch=j('source/state-patch-v1-contract.json')
profile_ext=j('verification/PROFILE_EXTENSIONS.json')
prog=y('source/program.ordo.yaml') or {}
module=y('source/modules/40_policies.ordo.module.yaml') or {}
tmpl=y('authoring_templates/reusable/DETERMINISTIC_FIRST_ARCHITECTURE.template.yaml') or {}
objs=(y('authoring/information_object_catalog.yaml') or {}).get('objects',[])
groups=(y('authoring/information_group_catalog.yaml') or {}).get('groups',[])
flows=(y('authoring/information_flow_graph.yaml') or {}).get('edges',[])
proj=(y('authoring/ordo_projection.yaml') or {}).get('information_bindings',[])

ck('policy_exists', bool(policy))
ck('policy_id', policy.get('policy_id')=='DETERMINISTIC_FIRST_ARCHITECTURE')
ck('scope_cross_domain', policy.get('scope')=='cross_domain')
ck('generated_inherit', policy.get('generated_playbooks_inherit') is True)

resp=policy.get('responsibility_ownership',{})
for cls in ['hashing','schema_validation','state_merge','patch_application','routing','counters','duplicate_detection','lifecycle_guards','coverage_accounting','package_integrity']:
 ck('det_owner_'+cls, resp.get(cls)=='deterministic')
ck('model_reasoning_only', set(policy.get('model_owned_classes',[])) >= {'semantic_interpretation','ambiguous_classification','natural_language_synthesis','hypothesis_generation'})

sp=policy.get('state_patch',{})
ck('state_patch_v1', sp.get('contract')=='state_patch_v1')
ck('patch_allowed_roots', sp.get('allowed_roots_required') is True)
ck('patch_base_hash', sp.get('base_state_hash_required') is True)
ck('patch_dependency_fp', sp.get('dependency_fingerprint_required_for_repeat_pass') is True)
ck('patch_fail_closed', sp.get('fail_closed_on_stale_baseline') is True)
ck('patch_no_whole_replace', sp.get('whole_state_replacement_default')=='forbidden')

boundary=policy.get('producer_boundary',{})
ck('validate_before_persist', boundary.get('validate_before_persist') is True)
ck('no_receipt_on_failure', boundary.get('no_transition_receipt_on_validation_failure') is True)
ck('current_node_unchanged', boundary.get('current_node_unchanged_on_validation_failure') is True)

mono=policy.get('monotonic_lifecycle',{})
ck('monotonic_guard', mono.get('deterministic_guard_required') is True)
ck('reopen_reason', mono.get('reopen_requires_evidence_bound_reason') is True)

recovery=policy.get('recovery_resume',{})
ck('recovery_deterministic', recovery.get('owner')=='deterministic')
ck('recovery_first_invalid', recovery.get('strategy')=='first_invalid_or_missing_milestone')
ck('resume_nonnull', recovery.get('resume_node_required_when_repairable') is True)

coverage=policy.get('machine_checkable_completeness',{})
ck('coverage_ids', coverage.get('stable_ids_required') is True)
ck('coverage_equal', coverage.get('acceptance_rule')=='required_ids_equals_accounted_for_ids')

hydr=policy.get('evidence_hydration',{})
ck('hydration_hash', hydr.get('source_hash_required') is True)
ck('hydration_allowlist', hydr.get('state_update_allowlist_required') is True)
ck('hydration_fail_closed', hydr.get('fail_closed_on_hash_or_schema_mismatch') is True)

sep=policy.get('state_context_separation',{})
ck('semantic_state_separate', sep.get('canonical_semantic_state')=='business_or_process_semantics_only')
ck('runtime_context_separate', sep.get('runtime_session_recovery_context_separate') is True)
ck('staging_not_semantic', sep.get('staging_status_is_not_semantic_fact') is True)

ck('state_patch_contract_file', patch.get('contract_id')=='state_patch_v1')
ck('state_patch_tool', (R/'tools/apply_state_patch_v1.py').is_file())
ck('hydration_tool', (R/'tools/hydrate_deterministic_evidence.py').is_file())
ck('architecture_validator', (R/'tools/validate_deterministic_first_architecture.py').is_file())

ck('template_exists', bool(tmpl))
ck('template_cross_domain', tmpl.get('scope')=='cross_domain')
required=set(tmpl.get('required_capabilities',[]))
for cap in ['RESPONSIBILITY_CLASSIFICATION','STATE_PATCH_V1','PRODUCER_BOUNDARY_VALIDATION','MONOTONIC_LIFECYCLE_GUARD','DETERMINISTIC_RECOVERY_RESUME','MACHINE_CHECKABLE_COMPLETENESS','SAFE_EVIDENCE_HYDRATION','STATE_CONTEXT_SEPARATION']:
 ck('template_'+cap.lower(), cap in required)

laws={x.get('id'):x for x in prog.get('playbook_laws',{}).get('laws',[]) if isinstance(x,dict)}
mlaws={x.get('id'):x for x in module.get('playbook_laws',{}).get('laws',[]) if isinstance(x,dict)}
ck('law_program', 'E92_DETERMINISTIC_FIRST_ARCHITECTURE' in laws)
ck('law_module', 'E92_DETERMINISTIC_FIRST_ARCHITECTURE' in mlaws)
ck('law_markdown', 'E92_DETERMINISTIC_FIRST_ARCHITECTURE' in (R/'PLAYBOOK_LAWS.md').read_text(encoding='utf-8'))

obj_ids={x.get('id') for x in objs if isinstance(x,dict)}
ck('data_object', 'I_DETERMINISTIC_FIRST_ARCHITECTURE_CONTRACT' in obj_ids)
g={x.get('id'):x for x in groups if isinstance(x,dict)}
ck('group_membership', 'I_DETERMINISTIC_FIRST_ARCHITECTURE_CONTRACT' in g.get('G_BUILD',{}).get('members',[]))
flow_t={(x.get('from'),x.get('to'),x.get('type')) for x in flows if isinstance(x,dict)}
ck('flow_resp_to_arch', ('I_DETERMINISTIC_EXECUTION_RESPONSIBILITY_CONTRACT','I_DETERMINISTIC_FIRST_ARCHITECTURE_CONTRACT','depends_on') in flow_t)
ck('flow_tool_to_arch', ('I_DETERMINISTIC_TOOL_RESULT_CONTRACT','I_DETERMINISTIC_FIRST_ARCHITECTURE_CONTRACT','depends_on') in flow_t)
ck('projection_binding', any(x.get('information_id')=='I_DETERMINISTIC_FIRST_ARCHITECTURE_CONTRACT' and {'N_B_NODE_ACTION_SYNTHESIS','N_B_GRAPH_RECOVERY_WIRING','N_VERIFY_REGRESSION'}.issubset(set(x.get('node_ids',[]))) for x in proj if isinstance(x,dict)))

laws_inherit={x.get('id') for x in inherit.get('laws',[]) if isinstance(x,dict)}
for rid in ['STATE_PATCH_V1_AT_MODEL_BOUNDARY','FAIL_CLOSE_AT_PRODUCER_BOUNDARY','MONOTONIC_LIFECYCLE_ENFORCEMENT','DETERMINISTIC_RECOVERY_RESUME','MACHINE_CHECKABLE_COMPLETENESS','SAFE_EVIDENCE_HYDRATION','STATE_CONTEXT_SEPARATION']:
 ck('inherit_'+rid.lower(), rid in laws_inherit)
ck('inherit_template', inherit.get('deterministic_first_architecture_template')=='authoring_templates/reusable/DETERMINISTIC_FIRST_ARCHITECTURE.template.yaml')

profiles=safe.get('profiles',{})
ck('model_patch_contract', 'state_patch_v1' in ' '.join(profiles.get('MODEL_AUTOMATIC',{}).get('conditional_requirements',[])))
ck('det_run_envelope', 'state_updates_v1' in ' '.join(profiles.get('DETERMINISTIC_RUN',{}).get('required',[])))
ck('gate_recovery_resume', 'recovery resume' in ' '.join(profiles.get('DETERMINISTIC_GATE',{}).get('conditional_requirements',[])).lower())


ck('profile_registration', any(x.get('id')=='alpha45_deterministic_first_architecture' for x in profile_ext.get('checks',[]) if isinstance(x,dict)))

# Behavioral contract checks for generic deterministic adapters.
try:
    import importlib.util
    def loadmod(name, rel):
        spec=importlib.util.spec_from_file_location(name, R/rel); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
    ap=loadmod('apply_state_patch_v1','tools/apply_state_patch_v1.py')
    hd=loadmod('hydrate_deterministic_evidence','tools/hydrate_deterministic_evidence.py')
    state={'a':{'x':1},'b':{'keep':True}}
    bp=ap.canon_sha(state)
    _,env=ap.apply_patch(state,{'contract':'state_patch_v1','base_state_sha256':bp,'dependency_fingerprint':'fp','allowed_roots':['a'],'set':{'/a/x':2}})
    ck('behavior_patch_pass', env.get('status')=='PASS' and env.get('state_updates')=={'a':{'x':2}})
    ck('behavior_patch_unrelated_preserved', 'b' not in env.get('state_updates',{}))
    try: ap.apply_patch(state,{'contract':'state_patch_v1','base_state_sha256':'bad','allowed_roots':['a'],'set':{'/a/x':2}}); stale=False
    except Exception: stale=True
    ck('behavior_patch_stale_fail', stale)
    try: ap.apply_patch(state,{'contract':'state_patch_v1','base_state_sha256':bp,'allowed_roots':['a'],'set':{'/b/x':2}}); outside=False
    except Exception: outside=True
    ck('behavior_patch_allowlist_fail', outside)
    import tempfile, hashlib
    with tempfile.TemporaryDirectory() as td:
        ep=Path(td)/'evidence.json'; ep.write_text(json.dumps({'state_updates':{'safe':{'v':1}}}),encoding='utf-8')
        sha=hashlib.sha256(ep.read_bytes()).hexdigest(); h=hd.hydrate(ep,sha,['safe'])
        ck('behavior_hydration_pass', h.get('state_updates')=={'safe':{'v':1}})
        try: hd.hydrate(ep,'bad',['safe']); badhash=False
        except Exception: badhash=True
        ck('behavior_hydration_hash_fail', badhash)
        try: hd.hydrate(ep,sha,['other']); badallow=False
        except Exception: badallow=True
        ck('behavior_hydration_allowlist_fail', badallow)
except Exception:
    for k in ['behavior_patch_pass','behavior_patch_unrelated_preserved','behavior_patch_stale_fail','behavior_patch_allowlist_fail','behavior_hydration_pass','behavior_hydration_hash_fail','behavior_hydration_allowlist_fail']:
        ck(k,False)

failed=[k for k,v in checks.items() if not v]
print(json.dumps({'status':'PASS' if not failed else 'FAIL','passed':sum(checks.values()),'total':len(checks),'failed':failed},indent=2,ensure_ascii=False))
raise SystemExit(0 if not failed else 1)
