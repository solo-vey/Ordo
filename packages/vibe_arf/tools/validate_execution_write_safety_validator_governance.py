#!/usr/bin/env python3
from pathlib import Path
import json,yaml,sys
R=Path(__file__).resolve().parents[1]
errs=[]
def req(cond,msg):
 if not cond: errs.append(msg)
try: p=json.loads((R/'source/execution-write-safety-validator-governance-policy.json').read_text())
except Exception as e: print('FAIL policy parse',e); sys.exit(1)
req(p.get('scope')=='cross_domain','scope must be cross_domain')
vi=p.get('validator_introspection',{}); req(vi.get('implementation_or_schema_before_heuristic_fix') is True,'validator introspection order missing'); req(vi.get('heuristic_fix_forbidden_when_contract_available') is True,'heuristic repair must fail closed')
wb=p.get('planned_write_boundary',{}); req(wb.get('unplanned_write_during_investigation_forbidden') is True,'unplanned investigation write not forbidden'); req(wb.get('new_write_requires_new_plan_risk_approval') is True,'new probe write lacks re-plan/re-approval')
ws=p.get('write_semantics_contract',{}); req(set(ws.get('allowed_modes',[]))=={'patch','merge','full_replace'},'write modes incomplete')
fr=ws.get('full_replace_requirements',{}); needed=['fresh_current_state','full_target_materialization','canonical_scope_identity','drift_guard','pre_change_backup','destructive_effect_disclosure','explicit_human_approval','post_state_verification']; req(all(fr.get(x) is True for x in needed),'full_replace safeguards incomplete')
sc=p.get('canonical_reviewed_scope',{}); req(sc.get('baseline_fingerprint_scope_must_equal_reviewed_scope') is True and sc.get('preapply_capture_scope_must_equal_reviewed_scope') is True and sc.get('scope_mismatch_blocks_write') is True,'scope identity guard incomplete')
ps=p.get('post_state_semantic_success',{}); req(ps.get('transport_success_is_not_semantic_success') is True and ps.get('success_claim_forbidden_before_post_state_verification') is True,'post-state semantic success guard incomplete')
sv=p.get('semantic_value_kinds',{}); req(set(sv.get('allowed',[]))=={'literal_text','translation_key','identifier','enum','opaque'},'semantic value kinds incomplete'); req(sv.get('pre_write_validation_required') is True,'semantic value kind prewrite validation missing')
for rel in p.get('schemas',{}).values(): req((R/rel).is_file(),f'missing schema {rel}')
# Full-replace JSON schema must conditionally require safeguards.
wschema=json.loads((R/'source/write-operation-contract.schema.json').read_text()); req(bool(wschema.get('allOf')),'write schema lacks full_replace conditional')
# Information model exposes semantic kind contract.
info=yaml.safe_load((R/'authoring/information_object_catalog.yaml').read_text()) or {}; req('semantic_value_kind_contract' in info,'Data Layer semantic kind contract missing')
if errs:
 for e in errs: print('FAIL',e)
 print(f'EXECUTION WRITE SAFETY VALIDATOR GOVERNANCE: FAIL ({len(errs)})'); sys.exit(1)
print('EXECUTION WRITE SAFETY VALIDATOR GOVERNANCE: PASS')
