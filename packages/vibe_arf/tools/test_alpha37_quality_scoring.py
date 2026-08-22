from pathlib import Path
import json, subprocess, sys, tempfile, yaml
R=Path(__file__).resolve().parents[1]
errors=[]

def ck(cond,msg):
    if not cond: errors.append(msg)

p=yaml.safe_load((R/'source/program.ordo.yaml').read_text(encoding='utf-8'))
q=json.loads((R/'source/quality_acceptance_policy.json').read_text(encoding='utf-8'))
a=json.loads((R/'source/autonomous-playbook-improvement-policy.json').read_text(encoding='utf-8'))
ids={x.get('id'):x for x in p.get('playbook_laws',{}).get('laws',[])}
nodes={x.get('id'):x for x in p.get('nodes',[])}
ck(str(p['ordo']['package_version']).startswith('0.1.'),'version is not repository-native Vibe semver')
ck(q.get('format') in ('vibe-quality-acceptance-policy/v4','vibe-quality-acceptance-policy/v5','vibe-quality-acceptance-policy/v6','vibe-quality-acceptance-policy/v7','vibe-quality-acceptance-policy/v8'),'quality policy unsupported')
ps=q.get('process_score',{})
ck(ps.get('starting_points')==1000,'process starts !=1000')
pen=ps.get('penalties',{})
expected_pen={
 'open_question':30,'startup_full_information':500,'open_question_cross_group_2_groups':70,
 'open_question_each_group_after_2':50,'group_collapse_per_group_when_2_or_more':100,
 'excess_independent_fact_after_10':5,'source_derivable_technical_fact_requested':25,
 'no_partial_information_path':150,'reasked_known_information':50,'nonadaptive_question':30,
 'prefilled_confirmation':5,'prefilled_confirmation_cross_group':15}
for k,v in expected_pen.items():
    ck(pen.get(k)==v,f'process penalty {k} != {v}')
rs=q.get('result_score',{})
ck(rs.get('starting_points_per_document')==1000,'result doc starts !=1000')
ck(rs.get('penalties',{}).get('missing_major_part')==100,'major part penalty !=100')
ck(rs.get('penalties',{}).get('missing_or_incomplete_detail')==10,'detail penalty !=10')
ck(rs.get('technical_documents')=='excluded','technical docs not excluded')
ck(rs.get('reference_variants',{}).get('selection')=='relevance_weighted_consensus_with_explicit_conflict_handling','reference variant selection is not relevance-weighted consensus')
final=q.get('final_score',{})
ck('process_score' in final.get('formula','') and ('development' in final.get('formula','') or 'result_score' in final.get('formula','')),'final formula mismatch')
ck('(process_score + 2 *' in final.get('equivalent_formula',''),'equivalent formula mismatch')
term=a.get('termination',{})
term_rule=term.get('rule','')
ck(term_rule.startswith('stop_after_three_consecutive_') and 'evaluated' in term_rule and 'above_current_best' in term_rule and 'protected-dimension eligibility first' in term.get('best_comparison','') and 'strictly greater development_score' in term.get('best_comparison',''), 'termination rule mismatch')
ck(term.get('streak_limit')==3,'streak limit !=3')
ck(term.get('example_scores')==[917,905,907],'termination example mismatch')
ck('quality_target' not in term and 'success' not in term,'threshold-based termination still present')
ck('E31_NORMALIZED_PLAYBOOK_QUALITY_SCORE' in ids,'E31 missing')
ck('E32_THREE_RUN_BEST_SCORE_STAGNATION' in ids,'E32 missing')
ck((R/'tools/calculate_playbook_quality_score.py').exists(),'deterministic scorer missing')
ck((R/'source/development-timing-policy.json').exists(),'timing policy missing')
# node routing semantics
ck('targets_reached' not in nodes.get('N_AI_DECIDE',{}).get('allowed_answers',[]),'targets_reached still allowed')
ck('stagnation_stop' in nodes.get('N_AI_DECIDE',{}).get('allowed_answers',[]),'stagnation_stop route missing')
# Execute scorer if available.
scorer=R/'tools/calculate_playbook_quality_score.py'
if scorer.exists():
    fixture={
      'evidence_tier':'live_acceptance',
      'result_eligibility':{'status':'PASS','result_scoring_eligible':True},
      'process':{
        'startup_interaction':{
          'requires_analyst_information':True,
          'contains_all_or_nearly_all_required_information':True,
          'represented_in_open_questions':True,
          'groups':['A','B','C']
        },
        'open_questions':[{'id':'q1','groups':['A','B','C']}],
        'prefilled_confirmations':[{'id':'c1','groups':['A','B']}],
        'group_collapse_groups':[3],
        'distinct_variables':['v1','v2','v3','v4'],
        'analyst_independent_facts':15,
        'source_derivable_technical_facts_requested':2,
        'no_partial_information_path':True,
        'reasked_known_information_count':1,
        'nonadaptive_question_count':1
      },
      'result_documents':[
        {'id':'d1','technical':False,'artifact_lineage_valid_for_development':True,'reference_variants':[
          {'id':'r1','missing_major_parts':1,'missing_or_incomplete_details':2},
          {'id':'r2','missing_major_parts':0,'missing_or_incomplete_details':3}
        ]},
        {'id':'tech','technical':True,'artifact_lineage_valid_for_development':True,'reference_variants':[{'id':'x','missing_major_parts':9,'missing_or_incomplete_details':9}]}
      ]
    }
    with tempfile.TemporaryDirectory() as td:
        inp=Path(td)/'in.json'; out=Path(td)/'out.json'; inp.write_text(json.dumps(fixture),encoding='utf-8')
        cp=subprocess.run([sys.executable,str(scorer),str(inp),str(out)],capture_output=True,text=True)
        ck(cp.returncode==0,'scorer execution failed: '+cp.stderr)
        if out.exists():
            o=json.loads(out.read_text())
            # family caps bound optimizer incentives and process score is floored at zero.
            ck(o['process_score']==0,'process score floor expected 0')
            ck(o.get('effective_process_penalties') is not None,'effective capped penalty view missing')
            # legacy count-only variants are interpreted as equal-reference consensus; mechanical penalties average to 75 => result 925.
            rscore=o.get('development_result_score',o.get('result_score')); fscore=o.get('development_score',o.get('playbook_score'))
            ck(rscore==925,'result score expected 925 under equal-reference consensus')
            ck(abs(fscore-616.666667)<1e-6,'final score expected 616.666667 with process floor')
if errors:
    print('ALPHA37 QUALITY SCORING: FAIL')
    for e in errors: print('-',e)
    sys.exit(1)
print('ALPHA37 QUALITY SCORING: PASS')
