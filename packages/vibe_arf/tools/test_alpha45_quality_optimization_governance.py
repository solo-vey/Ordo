#!/usr/bin/env python3
from pathlib import Path
import json,yaml,sys
R=Path(__file__).resolve().parents[1]
checks={}
def ck(k,v): checks[k]=bool(v)
def j(rel):
 p=R/rel; return json.loads(p.read_text()) if p.is_file() else {}
def y(rel):
 p=R/rel; return yaml.safe_load(p.read_text()) if p.is_file() else {}
pol=j('source/quality-optimization-governance-policy.json')
ck('policy_exists',bool(pol)); ck('policy_id',pol.get('policy_id')=='QUALITY_OPTIMIZATION_GOVERNANCE'); ck('scope',pol.get('scope')=='cross_domain')
for d in ['correctness','safety_authority','efficiency','artifact_quality']:
 ck('dimension_'+d,d in pol.get('acceptance_dimensions',{}))
ck('dimensions_not_collapsed',pol.get('dimension_rules',{}).get('no_single_dimension_substitution') is True)
ck('hard_law_no_reward',pol.get('calibration',{}).get('hard_law_compliance_reward')==0)
ck('uncalibrated_zero',pol.get('calibration',{}).get('uncalibrated_diagnostic_score_effect')==0)
ck('reward_penalty_evidence',pol.get('calibration',{}).get('numeric_score_effect_requires_calibration_evidence') is True)
ck('best_not_latest',pol.get('candidate_selection',{}).get('latest_is_best_by_default') is False)
ck('best_valid_only',pol.get('candidate_selection',{}).get('best_so_far_requires_valid_candidate') is True)
ck('quality_blocks_perf',pol.get('optimization_acceptance',{}).get('reject_if_any_protected_quality_dimension_regresses') is True)
ck('end_to_end_acceptance',pol.get('optimization_acceptance',{}).get('end_to_end_improvement_required') is True)
ck('local_gain_insufficient',pol.get('optimization_acceptance',{}).get('local_metric_gain_alone_is_insufficient') is True)
required_hist=['problem','baseline_evidence','hypothesis','protected_invariants','regression_asset','change','comparison_evidence','measured_result','limitations','decision']
ck('history_fields',all(x in pol.get('optimization_history',{}).get('required_fields',[]) for x in required_hist))
ck('history_append_only',pol.get('optimization_history',{}).get('append_only') is True)
ck('opportunity_zero',pol.get('degradation_diagnostics',{}).get('score_effect')==0)
ck('diag_time', 'time_degradation' in pol.get('degradation_diagnostics',{}).get('signals',[]))
ck('diag_token', 'token_degradation' in pol.get('degradation_diagnostics',{}).get('signals',[]))
ck('diag_pass', 'pass_count_degradation' in pol.get('degradation_diagnostics',{}).get('signals',[]))
for rel in ['authoring_templates/reusable/QUALITY_OPTIMIZATION_GOVERNANCE.template.yaml','tools/validate_quality_optimization_governance.py','source/optimization-history.schema.json']:
 ck('asset_'+Path(rel).name,(R/rel).is_file())
prog=y('source/program.ordo.yaml') or {}; mod=y('source/modules/40_policies.ordo.module.yaml') or {}
laws={x.get('id'):x for x in prog.get('playbook_laws',{}).get('laws',[]) if isinstance(x,dict)}
mlaws={x.get('id'):x for x in mod.get('playbook_laws',{}).get('laws',[]) if isinstance(x,dict)}
ck('law_program','E95_QUALITY_OPTIMIZATION_GOVERNANCE' in laws); ck('law_module','E95_QUALITY_OPTIMIZATION_GOVERNANCE' in mlaws); ck('law_md','E95_QUALITY_OPTIMIZATION_GOVERNANCE' in (R/'PLAYBOOK_LAWS.md').read_text())
reg=j('source/design_rule_incentive_registry.v1.json'); rr={x.get('id'):x for x in reg.get('rules',[]) if isinstance(x,dict)}
for rid in ['TOKEN_DEGRADATION','PASS_COUNT_DEGRADATION']:
 ck('registry_'+rid,rid in rr and rr[rid].get('score_effect')==0 and rr[rid].get('enforcement')=='OPPORTUNITY')
ck('perf_quality_guard',rr.get('QUALITY_REGRESSION_DURING_OPTIMIZATION',{}).get('enforcement')=='HARD_INELIGIBLE')
sub=j('source/performance-token-optimization-subprocess-policy.json')
ck('subprocess_history',sub.get('optimization_history_required') is True)
ck('subprocess_global_acceptance',sub.get('hard_rules',{}).get('local_gain_without_end_to_end_improvement_rejected') is True)
ext=j('verification/PROFILE_EXTENSIONS.json')
blob=json.dumps(ext)
ck('profile_registered','alpha45_quality_optimization_governance' in blob)
# Change 8 hardening: inheritance, propagation, template parity, best-so-far eligibility, append-only enforcement.
kit=j('authoring_templates/reusable/TEMPLATE_KIT_REGISTRY.json')
ck('kit_registered',kit.get('reusable_subprocesses',{}).get('QUALITY_OPTIMIZATION_GOVERNANCE')=='authoring_templates/reusable/QUALITY_OPTIMIZATION_GOVERNANCE.template.yaml')
ck('kit_instantiation_order',set(kit.get('instantiation_order',[]))==set(kit.get('templates',{})))
tpl=y('authoring_templates/reusable/QUALITY_OPTIMIZATION_GOVERNANCE.template.yaml') or {}
ck('template_same_regime',tpl.get('optimization_acceptance',{}).get('same_regime_comparison_required') is True)
ck('template_perf_equivalence',tpl.get('optimization_acceptance',{}).get('semantic_and_artifact_equivalence_required_for_performance_only_change') is True)
ck('template_platform_separation',tpl.get('optimization_acceptance',{}).get('platform_overhead_must_be_separated_from_playbook_controlled_cost') is True)
ck('template_dimension_reporting',tpl.get('dimension_rules',{}).get('protected_dimensions_must_be_reported_separately') is True)
ck('template_hard_guard_override',tpl.get('dimension_rules',{}).get('hard_guard_failure_overrides_numeric_score') is True)
ck('template_calibration_evidence',tpl.get('calibration',{}).get('numeric_score_effect_requires_calibration_evidence') is True and len(tpl.get('calibration',{}).get('calibration_evidence_requires',[]))>=5)
ck('template_invalid_cannot_replace_best',tpl.get('candidate_selection',{}).get('invalid_or_hard_ineligible_candidate_cannot_replace_best') is True)
ck('template_dimension_eligibility_before_score',tpl.get('candidate_selection',{}).get('protected_dimension_eligibility_precedes_numeric_ranking') is True)
for rel in ['canonical_support/guides/PLAYBOOK_LAWS.md','canonical_support/output_templates/PLAYBOOK_LAWS.md']:
 ck('propagation_'+Path(rel).parent.name,'E95_QUALITY_OPTIMIZATION_GOVERNANCE' in (R/rel).read_text())
auto=j('source/autonomous-playbook-improvement-policy.json')
ck('best_so_far_dimension_eligible','protected-dimension-eligible' in auto.get('best_so_far',{}).get('ranking_rule',''))
ck('best_so_far_score_cannot_override','never override' in auto.get('best_so_far',{}).get('ranking_rule',''))
ck('termination_eligibility_first','eligibility first' in auto.get('termination',{}).get('best_comparison',''))
ck('e95_eligibility_before_score','protected-dimension non-regression are evaluated before numeric ranking' in (R/'PLAYBOOK_LAWS.md').read_text())
ledger=j('source/optimization-history-ledger.json')
ck('history_ledger_exists',bool(ledger) and ledger.get('append_only') is True)
ck('history_hash_chained',pol.get('optimization_history',{}).get('hash_chained') is True and tpl.get('optimization_history',{}).get('hash_chained') is True)
ck('history_validator_asset',(R/'tools/validate_optimization_history_ledger.py').is_file())
passed=sum(checks.values()); total=len(checks)
for k,v in checks.items(): print(('PASS' if v else 'FAIL'),k)
print(f'ALPHA45 QUALITY OPTIMIZATION GOVERNANCE: {passed}/{total} PASS')
sys.exit(0 if passed==total else 1)
