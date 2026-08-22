#!/usr/bin/env python3
import json,sys,pathlib,yaml
root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else pathlib.Path(__file__).resolve().parents[1])
q=json.loads((root/'source/quality_acceptance_policy.json').read_text())
a=json.loads((root/'source/autonomous-playbook-improvement-policy.json').read_text())
laws=(root/'PLAYBOOK_LAWS.md').read_text()
mod=yaml.safe_load((root/'source/modules/30_vibe_architecture.ordo.module.yaml').read_text())
gmod=yaml.safe_load((root/'source/modules/60_validation_outputs.ordo.module.yaml').read_text())
ids={x.get('id') for x in mod.get('nodes',[])} | {x.get('id') for x in gmod.get('gates',[])}
req_nodes={
'N_AI_DISCOVER_ARTIFACT_EVAL_PROFILE','N_AI_SELECT_GOLDEN_REFERENCES','N_AI_BUILD_REFERENCE_PROFILE',
'G_AI_REFERENCE_CONFLICTS_RESOLVED','N_AI_BUILD_DYNAMIC_COMPARATIVE_PROMPT','N_AI_RUN_FRESH_COMPARATIVE_EVALUATOR',
'G_AI_FRESH_REFERENCE_FIDELITY','N_AI_SANITIZE_EVALUATION_DEFECTS'}
checks={}
checks['law_dynamic']='DYNAMIC_REFERENCE_EVALUATION' in laws
checks['law_multi']='MULTI_REFERENCE_REASONING' in laws
checks['law_fresh']='FRESH_DEFECT_DISCOVERY' in laws
checks['law_golden']='GOLDEN_REFERENCE_EVALUATOR_ONLY' in laws
h=q.get('result_score',{}).get('analytical_comparative_evaluator',{})
checks['dynamic_plan']=h.get('dynamic_prompt_from_artifact_and_references') is True
checks['multi_reference']=h.get('multiple_references')=='relevance_weighted_with_conflict_detection'
checks['fresh_discovery']=h.get('fresh_discovery_each_revision') is True
checks['no_false_1000']=h.get('perfect_score_gate')=='zero_known_and_zero_fresh_material_or_major_defects'
checks['evaluator_isolation']=h.get('evaluator_separate_from_generator_optimizer') is True
checks['sanitization']=h.get('golden_reference_visibility')=='evaluator_only_sanitized_remediation_to_optimizer'
checks['structured_output']=set(h.get('required_output',[])) >= {'reference_selection','dimension_scores','defects','freshly_discovered_defects','reference_conflicts','score_rationale','next_improvement_targets'}
checks['nodes']=req_nodes <= ids
checks['optimizer_input']='sanitized comparative defects' in a.get('quality_evaluation',{}).get('next_iteration_input','')
failed=[k for k,v in checks.items() if not v]
print(json.dumps({'status':'PASS' if not failed else 'FAIL','checks':checks,'failed':failed},indent=2))
sys.exit(0 if not failed else 1)
