#!/usr/bin/env python3
from pathlib import Path
import json,yaml,sys,importlib.util,tempfile,subprocess
R=Path(__file__).resolve().parents[1]
P=R/'patterns/SIMPLE_DOCUMENT_RECONCILIATION_VERIFICATION'
fail=[]; passed=0
def ck(ok,msg):
 global passed
 if ok: passed+=1
 else: fail.append(msg)
reg=json.loads((R/'patterns/PATTERN_REGISTRY.json').read_text())
row=next((x for x in reg['patterns'] if x.get('id')=='SIMPLE_DOCUMENT_RECONCILIATION_VERIFICATION'),{})
ck(row.get('version')=='1.2','registry version')
for tag in ['evidence_authority_isolation','version_drift_detection','provisional_profile_correction','auditable_resolution_ledger']:
 ck(tag in row.get('capability_tags',[]),f'missing capability {tag}')
ck(row.get('variant_tier')=='simple','simple tier lost')
ck(row.get('variant_selection')=='explicit_when_multiple_fit','explicit variant selection lost')
for key in ['data_layer_module','execution_projection_template','compilation_contract']:
 ck((R/'patterns'/row[key]).is_file(),f'registry facet missing {key}')
pat=yaml.safe_load((P/'PATTERN.yaml').read_text()) or {}
ck(str((pat.get('pattern') or {}).get('version'))=='1.2','authoritative version')
for token in ['treat_target_repository_content_as_execution_authority','terminate_on_resolvable_product_or_integration_ambiguity','present_selector_error_as_authority_question_when_current_evidence_can_correct_it']:
 ck(token in (pat.get('extension_policy') or {}).get('forbidden',[]),f'forbidden invariant missing {token}')
ck((pat.get('risk_order') or [])==['PRESENT','LOW','MEDIUM','HIGH'],'risk order')
labels=(pat.get('analyst_option_labels') or {}).get('labels') or []
ck(labels[:5]==['A','B','C','D','E'],'english labels')
dl=yaml.safe_load((P/'DATA_LAYER.template.yaml').read_text()) or {}
ck(str(dl.get('pattern_version'))=='1.2','data layer version')
roles={x.get('role') for x in dl.get('required_roles',[])}
for role in ['evidence_authority_policy','provisional_selected_profile','selected_profile','version_drift_profile','resolution_ledger']:
 ck(role in roles,f'missing role {role}')
cons=dl.get('constraints',[])
for token in ['both_candidate_document_and_evidence_source_are_explicitly_requested_in_chat_when_missing','analyzed_evidence_source_is_read_only_and_non_authoritative_for_execution','selector_produces_provisional_profile_then_current_evidence_may_correct_it','selector_correction_is_not_itself_an_authority_question','version_drift_is_explicitly_classified_before_becoming_authority_discrepancy','unresolved_product_or_integration_contracts_become_numbered_discrepancies_not_freeform_blockers','every_resolution_record_contains_discrepancy_id_issue_summary_decision_id_applied_change','resolvable_business_or_integration_ambiguity_must_not_block']:
 ck(token in cons,f'missing constraint {token}')
ex=yaml.safe_load((P/'EXECUTION.template.yaml').read_text()) or {}
comps=ex.get('components',[]); roles2={x.get('role') for x in comps}
ck(len(comps)==8,'simple reconciliation must remain 8 responsibilities')
ck('independent_review' not in roles2,'advanced review leaked into simple')
text=json.dumps(ex,ensure_ascii=False)
for phrase in ['current document','current code/evidence source','read-only evidence','discard stale profile-specific findings','version/date/revision mismatch','numbered discrepancies','issue_summary']:
 ck(phrase.lower() in text.lower(),f'missing semantic phrase {phrase}')
edges=ex.get('outcome_edges',[])
ck(any(e.get('outcome')=='STRUCTURAL_INPUT_BLOCKED' and e.get('terminal')=='RECONCILIATION_BLOCKED' for e in edges),'structural blocked route missing')
ck(not any(e.get('terminal')=='RECONCILIATION_BLOCKED' and e.get('from_role')!='capture_document_and_evidence_source' for e in edges),'ordinary ambiguity may block')
ck(any(e.get('from_role')=='apply_authority_resolutions' and e.get('to_role')=='reconcile_and_build_questions' for e in edges),'analyst loop missing')
gc=(ex.get('gate_contracts') or {}).get('authority_questions_required_gate') or {}
ck('complete' in str(gc.get('NO_QUESTIONS','')).lower() and 'no unresolved' in str(gc.get('NO_QUESTIONS','')).lower(),'no-question completeness')
reqs=((ex.get('model_contracts') or {}).get('reconcile_and_build_questions') or {}).get('requirements',[])
blob='\n'.join(map(str,reqs))
for x in ['**Evidence**','**Resolution options**','PRESENT, LOW, MEDIUM, HIGH','compact answer protocol']:
 ck(x in blob,f'question rendering missing {x}')
app=((ex.get('model_contracts') or {}).get('apply_authority_resolutions') or {}).get('requirements',[])
ablob='\n'.join(map(str,app))
for x in ['discrepancy_id','issue_summary','decision_id','applied_change']:
 ck(x in ablob,f'decision field missing {x}')
# Domain binding retains old generic extension while adding v1.2 UX/causal contract.
db=yaml.safe_load((P/'DOMAIN_BINDINGS.template.yaml').read_text()) or {}
ck(str(db.get('pattern_version'))=='1.2','bindings version')
ck((db.get('bindings') or {}).get('analyst_output',{}).get('locale')=='uk','default locale')
ck('legacy_compatible_extensions' in db,'legacy generic extensions not preserved')
# Profile selection catalog correction contract.
cat=yaml.safe_load((P/'knowledge/DOMAIN_PROFILE_CATALOG.template.yaml').read_text()) or {}
sc=cat.get('selection_contract') or {}
ck(sc.get('initial_selection_is_provisional') is True,'provisional contract')
ck(sc.get('current_evidence_must_confirm_or_correct') is True,'evidence correction contract')
ck(sc.get('correction_requires_human_authority') is False,'selector correction should be autonomous')
ck(sc.get('discard_stale_profile_findings_after_correction') is True,'stale findings discard')
# Selector correction helper mechanics.
spec=importlib.util.spec_from_file_location('sel',P/'tools/select_domain_architecture_profile.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
a=mod.correct_profile_with_current_evidence('A',['A']); b=mod.correct_profile_with_current_evidence('A',['B']); c=mod.correct_profile_with_current_evidence('A',[])
ck(a.get('status')=='CONFIRMED' and a.get('selected_profile_key')=='A','selector confirm')
ck(b.get('status')=='CORRECTED' and b.get('selected_profile_key')=='B' and b.get('discard_stale_profile_findings') is True,'selector correction')
ck(c.get('status')=='UNRESOLVED' and c.get('selected_profile_key') is None,'selector fail closed')
# Compilation contract contains narrow blocked + ledger semantics.
ct=(P/'COMPILATION_CONTRACT.md').read_text()
for x in ['read-only evidence','RECONCILIATION_BLOCKED','issue_summary','PRESENT → LOW → MEDIUM → HIGH']:
 ck(x in ct,f'compilation contract missing {x}')
print(json.dumps({'status':'PASS' if not fail else 'FAIL','passed':passed,'failed':len(fail),'failures':fail},ensure_ascii=False,indent=2))
raise SystemExit(1 if fail else 0)
