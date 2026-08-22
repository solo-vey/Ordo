#!/usr/bin/env python3
from pathlib import Path
import json,yaml,sys
R=Path(__file__).resolve().parents[1]
checks={}
def ck(k,v): checks[k]=bool(v)
def j(rel):
 p=R/rel
 try:return json.loads(p.read_text())
 except:return {}
def y(rel):
 p=R/rel
 try:return yaml.safe_load(p.read_text()) or {}
 except:return {}
pol=j('source/execution-write-safety-validator-governance-policy.json')
ck('policy_exists', bool(pol))
ck('policy_id', pol.get('policy_id')=='EXECUTION_WRITE_SAFETY_VALIDATOR_GOVERNANCE')
vi=pol.get('validator_introspection',{})
ck('validator_id_first', vi.get('resolve_validator_id_before_repair') is True)
ck('validator_contract_first', vi.get('implementation_or_schema_before_heuristic_fix') is True)
ck('heuristic_forbidden_if_contract_available', vi.get('heuristic_fix_forbidden_when_contract_available') is True)
ck('machine_readable_expectations_preferred', vi.get('machine_readable_expectations_required_when_platform_supports') is True)
wb=pol.get('planned_write_boundary',{})
ck('unplanned_write_forbidden', wb.get('unplanned_write_during_investigation_forbidden') is True)
ck('new_probe_needs_plan', wb.get('new_write_requires_new_plan_risk_approval') is True)
ck('approved_plan_identity', wb.get('approved_change_plan_identity_required') is True)
ws=pol.get('write_semantics_contract',{})
ck('write_modes', set(ws.get('allowed_modes',[]))=={'patch','merge','full_replace'})
fr=ws.get('full_replace_requirements',{})
for k in ['fresh_current_state','full_target_materialization','canonical_scope_identity','drift_guard','pre_change_backup','destructive_effect_disclosure','explicit_human_approval','post_state_verification']:
 ck('full_replace_'+k, fr.get(k) is True)
sc=pol.get('canonical_reviewed_scope',{})
ck('scope_identity_required', sc.get('reviewed_scope_id_required') is True)
ck('scope_baseline_equal', sc.get('baseline_fingerprint_scope_must_equal_reviewed_scope') is True)
ck('scope_preapply_equal', sc.get('preapply_capture_scope_must_equal_reviewed_scope') is True)
ck('scope_mismatch_blocks_write', sc.get('scope_mismatch_blocks_write') is True)
ps=pol.get('post_state_semantic_success',{})
ck('transport_not_semantic', ps.get('transport_success_is_not_semantic_success') is True)
ck('fresh_post_state', ps.get('fresh_post_state_required') is True)
ck('semantic_compare', ps.get('semantic_target_verification_required') is True)
ck('no_success_without_post', ps.get('success_claim_forbidden_before_post_state_verification') is True)
sv=pol.get('semantic_value_kinds',{})
ck('semantic_kinds', set(sv.get('allowed',[]))=={'literal_text','translation_key','identifier','enum','opaque'})
ck('semantic_kind_prewrite', sv.get('pre_write_validation_required') is True)
ck('semantic_kind_data_layer', sv.get('data_layer_contract') is True)
for rel in ['authoring_templates/reusable/EXECUTION_WRITE_SAFETY_VALIDATOR_GOVERNANCE.template.yaml','tools/validate_execution_write_safety_validator_governance.py']:
 ck('asset_'+Path(rel).name,(R/rel).is_file())
kit=j('authoring_templates/reusable/TEMPLATE_KIT_REGISTRY.json')
ck('template_registered', kit.get('reusable_subprocesses',{}).get('EXECUTION_WRITE_SAFETY_VALIDATOR_GOVERNANCE')=='authoring_templates/reusable/EXECUTION_WRITE_SAFETY_VALIDATOR_GOVERNANCE.template.yaml')

# mechanical schema behavior
try:
 import jsonschema
 write_schema=j('source/write-operation-contract.schema.json')
 bad={'operation_id':'W1','approved_change_plan_id':'P1','reviewed_scope_id':'S1','write_semantics':'full_replace'}
 good={**bad,'baseline_fingerprint_scope_id':'S1','preapply_capture_scope_id':'S1','fresh_current_state_evidence':'E1','full_target_materialization_evidence':'E2','pre_change_backup_evidence':'E3','destructive_effect_disclosure_evidence':'E4','human_approval_evidence':'E5','post_state_verification_evidence':'E6'}
 try: jsonschema.validate(bad,write_schema); bad_rejected=False
 except Exception: bad_rejected=True
 try: jsonschema.validate(good,write_schema); good_accepted=True
 except Exception: good_accepted=False
 ck('full_replace_schema_rejects_incomplete',bad_rejected)
 ck('full_replace_schema_accepts_complete',good_accepted)
 vi_schema=j('source/validator-introspection-contract.schema.json')
 try: jsonschema.validate({'validator_id':'V1','contract_resolution_status':'RESOLVED','heuristic_fix_allowed':True},vi_schema); resolved_heuristic_rejected=False
 except Exception: resolved_heuristic_rejected=True
 ck('validator_schema_rejects_heuristic_when_resolved',resolved_heuristic_rejected)
 sv_schema=j('source/semantic-value-kind.schema.json')
 try: jsonschema.validate('free_text_guess',sv_schema); bad_kind_rejected=False
 except Exception: bad_kind_rejected=True
 ck('semantic_kind_schema_rejects_unknown',bad_kind_rejected)
except Exception:
 ck('full_replace_schema_rejects_incomplete',False); ck('full_replace_schema_accepts_complete',False); ck('validator_schema_rejects_heuristic_when_resolved',False); ck('semantic_kind_schema_rejects_unknown',False)

# law propagation
for rel in ['PLAYBOOK_LAWS.md','canonical_support/guides/PLAYBOOK_LAWS.md','canonical_support/output_templates/PLAYBOOK_LAWS.md','authoring_templates/PLAYBOOK_LAWS.md']:
 p=R/rel; ck('law_'+Path(rel).parent.name+'_'+Path(rel).name, p.is_file() and 'E96_EXECUTION_WRITE_SAFETY_VALIDATOR_GOVERNANCE' in p.read_text())
mod=y('source/modules/40_policies.ordo.module.yaml'); prog=y('source/program.ordo.yaml')
for name,d in [('module',mod),('program',prog)]:
 laws={x.get('id') for x in d.get('playbook_laws',{}).get('laws',[]) if isinstance(x,dict)}
 ck('law_'+name,'E96_EXECUTION_WRITE_SAFETY_VALIDATOR_GOVERNANCE' in laws)
# semantic value kind schema surfaced in authoring information objects
info=y('authoring/information_object_catalog.yaml')
objs=info.get('objects',[])+info.get('information_objects',[])
ck('catalog_semantic_kind_contract', any(isinstance(o,dict) and isinstance(o.get('value_contract'),dict) and 'semantic_value_kind' in o['value_contract'] for o in objs))
# validators and profile
ext=j('verification/PROFILE_EXTENSIONS.json'); ck('profile_registered','alpha46_execution_write_safety_validator_governance' in json.dumps(ext))
passed=sum(checks.values()); total=len(checks)
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f'ALPHA46 EXECUTION WRITE SAFETY VALIDATOR GOVERNANCE: {passed}/{total} PASS')
sys.exit(0 if passed==total else 1)
