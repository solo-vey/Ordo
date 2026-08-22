#!/usr/bin/env python3
import json, pathlib, sys, yaml
R=pathlib.Path(__file__).resolve().parents[1]
checks=[]
def ck(name, cond, detail=''):
    checks.append((name,bool(cond),detail))

def j(path):
    p=R/path
    return json.loads(p.read_text()) if p.exists() else {}

def y(path):
    p=R/path
    return yaml.safe_load(p.read_text()) if p.exists() else {}

ctxp=R/'source/analyst-context-preservation-policy.json'
ctx=j('source/analyst-context-preservation-policy.json')
ck('context_policy_exists', ctxp.exists())
ck('production_context_required', ctx.get('production_package_surface')=='analyst_context')
ck('retention_modes', set(ctx.get('retention_modes',{})) >= {'embed_authoritative','embed_evaluator_only','summary_plus_refresh_record','metadata_only'})
ck('volatile_large_requires_refresh', ctx.get('volatile_or_large_source',{}).get('must_mark_refresh_required') is True)
ck('field_provenance_required', ctx.get('provenance',{}).get('field_or_item_level') is True)
ck('golden_evaluator_only', ctx.get('reference_access',{}).get('full_golden_visibility')=='evaluator_only')
ck('context_catalog_required', 'analyst_context/context_catalog.json' in ctx.get('required_files',[]))
ck('capture_tool_exists', (R/'tools/capture_analyst_context.py').exists())
ck('context_validator_exists', (R/'tools/validate_analyst_context.py').exists())

pc=j('PRODUCTION_PACKAGE_CONTRACT.json')
classes={x.get('class'):x for x in pc.get('artifact_classes',[]) if isinstance(x,dict)}
ck('production_package_has_analyst_context_class', 'analyst_context' in classes)
ck('analyst_context_required_in_production', classes.get('analyst_context',{}).get('default_inclusion')=='required')
_profiles=j('source/generated-playbook-production-package-policy.json').get('package_profiles',{})
_prod=_profiles.get('production',{})
_eff=_profiles.get(_prod.get('alias_of'),{}) if _prod.get('alias_of') else _prod
ck('production_policy_required_surface', 'analyst_context' in _eff.get('required_surfaces',[]))

opt=j('source/autonomous-playbook-improvement-policy.json')
term=opt.get('termination',{})
reg=opt.get('evaluation_regime',{})
ck('frozen_evaluation_regime', reg.get('frozen_within_run') is True and all(k in reg.get('identity_fields',[]) for k in ['scorer_version','reference_set_hash','prompt_builder_version','aggregation_policy_version','stagnation_threshold']))
return_rule=opt.get('best_so_far',{}).get('return_rule','')
ck('best_not_latest', return_rule.startswith('highest_scoring_valid_revision') and 'development_score' in return_rule)
ck('stagnation_resets_zero', term.get('on_strict_improvement_streak')==0)
ck('invalid_no_stagnation', term.get('invalid_revision_counts_toward_stagnation') is False)
ck('no_1000_target', term.get('score_1000_is_required_target') is False)
ck('fresh_and_regression_separate', opt.get('quality_evaluation',{}).get('known_defect_regression_phase')=='separate_after_fresh_discovery')
ck('consensus_not_identity', opt.get('quality_evaluation',{}).get('multi_reference_objective')=='relevance_weighted_consensus_quality')
ck('unsupported_reference_fact_no_fabrication', opt.get('quality_evaluation',{}).get('unsupported_reference_fact_policy')=='SOURCE_EVIDENCE_REQUIRED_not_optimizer_fabrication')
ck('evidence_aware_remediation', set(opt.get('quality_evaluation',{}).get('remediation_types',[])) >= {'PLAYBOOK_CAPABILITY','SOURCE_EVIDENCE_REQUIRED'})
ck('invalid_revision_no_score', opt.get('quality_evaluation',{}).get('invalid_revision_scoring')=='ineligible_no_score')
ck('offline_live_separate', opt.get('quality_evaluation',{}).get('offline_live_separation')=='development_optimum_is_not_live_acceptance')
ck('package_no_sim_leakage', 'generated simulation outputs and evaluator-only evidence' in ' '.join(j('source/generated-playbook-production-package-policy.json').get('principles',[])).lower() or 'simulation_outputs' in j('source/generated-playbook-production-package-policy.json').get('package_profiles',{}).get('production',{}).get('excluded_classes',[]))

objs=y('authoring/information_object_catalog.yaml').get('objects',[])
ids={o.get('id') for o in objs if isinstance(o,dict)}
ck('canonical_context_object', 'I_ANALYST_CONTEXT_PRESERVATION_CONTRACT' in ids)
ck('canonical_optimization_object', 'I_OPTIMIZATION_LOOP_CALIBRATION_CONTRACT' in ids)

failed=[x for x in checks if not x[1]]
for n,ok,d in checks: print(('PASS' if ok else 'FAIL'),n, d)
print(f'{len(checks)-len(failed)}/{len(checks)} PASS')
sys.exit(1 if failed else 0)
