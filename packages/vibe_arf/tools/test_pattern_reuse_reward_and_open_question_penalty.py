#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys, tempfile, shutil, yaml
R=Path(__file__).resolve().parents[1]
fail=[]; passed=0

def ck(c,m):
    global passed
    if c: passed+=1
    else: fail.append(m)

q=json.loads((R/'source/quality_acceptance_policy.json').read_text())
ps=q.get('process_score',{})
ck(ps.get('penalties',{}).get('open_question')==30,'open question penalty must be 30')
ck(ps.get('rewards',{}).get('qualified_reusable_pattern')==50,'qualified reusable pattern reward must be +50')
cc=ps.get('counting_contract',{})
ck('interaction' in str(cc.get('open_question','')).lower(),'open-question counting must be per interaction')
ck('additional' in str(cc.get('open_question','')).lower() and '10' in str(cc.get('open_question','')),'open-question contract must state -10 per additional variable')
rr=ps.get('reward_contract',{})
ck(rr.get('qualified_reusable_pattern',{}).get('requires_mechanical_verification') is True,'pattern reward must require mechanical verification')
ck(rr.get('qualified_reusable_pattern',{}).get('duplicate_semantic_responsibility_reward') is False,'duplicate reuse reward must be forbidden')
ck('graph realization' in str(rr.get('qualified_reusable_pattern',{}).get('requires','')).lower(),'pattern reward contract must require final graph realization')
ck(rr.get('qualified_reusable_pattern',{}).get('blueprint_only_reward')=='forbidden','blueprint-only reuse reward must be forbidden')
ck(rr.get('missed_pattern_opportunity',{}).get('score_effect')==0,'missed pattern opportunity must be reward opportunity, not hidden penalty')
ck((R/'tools/evaluate_pattern_reuse_opportunities.py').exists(),'missing deterministic pattern reuse opportunity evaluator')

scorer=R/'tools/calculate_playbook_quality_score.py'
base_doc={'id':'d','technical':False,'artifact_lineage_valid_for_development':True,'reference_variants':[{'id':'r','missing_major_parts':0,'missing_or_incomplete_details':0}]}

def run(proc):
    fixture={'evidence_tier':'offline_conformance','result_eligibility':{'status':'FAIL','result_scoring_eligible':False},'process':proc,'result_documents':[base_doc]}
    with tempfile.TemporaryDirectory() as td:
        i=Path(td)/'in.json'; o=Path(td)/'out.json'; i.write_text(json.dumps(fixture))
        cp=subprocess.run([sys.executable,str(scorer),str(i),str(o)],capture_output=True,text=True)
        return cp, json.loads(o.read_text()) if o.exists() else None

# One open interaction: first variable costs 30, every additional variable costs 10.
cp,o=run({'open_questions':[{'id':'q1','parameter_ids':['a','b','c'],'groups':['A']}],'prefilled_confirmations':[],'distinct_variables':[]})
ck(cp.returncode==0,'scorer failed on one open question')
if o:
    ck(o['process_penalties']['open_question']==30,'base open-question penalty must remain 30')
    ck(o['process_penalties'].get('open_question_additional_variable')==20,'three variables in one open question must add 20')

# Current working Vibe dogfoods both selected reusable patterns.
# It must earn +100 only when both exact graph realizations remain valid.
cp,o=run({'open_questions':[{'id':'q1','parameter_ids':['a']},{'id':'q2','parameter_ids':['b','c']}],'prefilled_confirmations':[],'distinct_variables':[],'pattern_reuse_candidate_root':str(R)})
ck(cp.returncode==0,'scorer failed on current-root reuse audit: '+cp.stderr)
if o:
    ck(o['process_penalties']['open_question']==60,'two open interactions must cost base 60')
    ck(o['process_penalties'].get('open_question_additional_variable')==10,'second interaction with two variables must add 10')
    ck(o.get('process_rewards',{}).get('qualified_reusable_pattern')==100,'two exact graph-realized self reuses must earn +100')
    ck(o['process_score']==1030,'process score must be 1000 - 60 - 10 + 100 for two realized reusable patterns')
    opp=o.get('consolidated_improvement_opportunities',[])
    ck(not any(x.get('pattern_instance_id') in {'PI_BUSINESS_VIEW_DOCUMENT','PI_GENERATED_PLAYBOOK_PACKAGE'} for x in opp),'fully realized selected self patterns must not remain optimizer opportunities')

# Build exact graph realization from the frozen projection: two distinct qualified reuses => +100.
with tempfile.TemporaryDirectory() as td:
    root=Path(td); (root/'patterns').mkdir(); (root/'authoring').mkdir(); (root/'source').mkdir()
    shutil.copytree(R/'patterns',root/'patterns',dirs_exist_ok=True)
    for name in ['pattern_selection_input_snapshot.json','capability_requirement_catalog.yaml','pattern_instance_catalog.yaml','pattern_execution_projection.yaml','artifact_catalog.yaml','information_object_catalog.yaml','information_group_catalog.yaml','information_flow_graph.yaml','interaction_projection.yaml']:
        shutil.copy(R/'authoring'/name,root/'authoring'/name)
    proj=yaml.safe_load((root/'authoring/pattern_execution_projection.yaml').read_text()) or {}
    comp={}; outgoing={}; incoming={}
    for f in proj.get('fragments',[]):
        for c in f.get('components',[]): comp[c['component_id']]=c
        for e in f.get('edges',[]):
            outgoing.setdefault(e['from'],[]).append(e['to']); incoming.setdefault(e['to'],[]).append(e['from'])
    nodes=[]; gates=[]
    for cid,c in comp.items():
        if c['kind']=='node':
            n={'id':cid,'question':'pattern role '+c['role'],'answer_type':'structured_record','allowed_from':incoming.get(cid,[])}
            if outgoing.get(cid): n['on_answer']={'update_state':{},'next':outgoing[cid][0]}
            nodes.append(n)
        else:
            gates.append({'id':cid,'method':'mechanical','trust_class':'deterministic','condition':'true','on_pass':outgoing.get(cid,['END'])[0],'on_fail':'STOP','allowed_from':incoming.get(cid,[])})
    (root/'source/program.ordo.yaml').write_text(yaml.safe_dump({'nodes':nodes,'gates':gates},sort_keys=False))
    cp,o=run({'open_questions':[],'prefilled_confirmations':[],'distinct_variables':[],'pattern_reuse_candidate_root':str(root)})
    ck(cp.returncode==0,'scorer failed on realized reward fixture: '+cp.stderr)
    if o:
        ck(o.get('process_rewards',{}).get('qualified_reusable_pattern')==100,'two exact graph-realized reuses must reward 100')
        ck(o['process_score']==1100,'two qualified reuses must produce raw process score 1100')

# Remove one pattern binding: it must remain a zero-penalty +50 opportunity even if another pattern is realized.
with tempfile.TemporaryDirectory() as td:
    root=Path(td); (root/'patterns').mkdir(); (root/'authoring').mkdir(); (root/'source').mkdir()
    shutil.copytree(R/'patterns',root/'patterns',dirs_exist_ok=True)
    for name in ['pattern_selection_input_snapshot.json','capability_requirement_catalog.yaml','pattern_instance_catalog.yaml','pattern_execution_projection.yaml','information_object_catalog.yaml','information_group_catalog.yaml','information_flow_graph.yaml','interaction_projection.yaml']:
        shutil.copy(R/'authoring'/name,root/'authoring'/name)
    arts=yaml.safe_load((R/'authoring/artifact_catalog.yaml').read_text())
    for a in arts['artifacts']:
        if a['id']=='A_GENERATED_PLAYBOOK_PACKAGE': a.pop('pattern_binding',None)
    (root/'authoring/artifact_catalog.yaml').write_text(yaml.safe_dump(arts,sort_keys=False))
    # Remove the corresponding selected instance and rederive the projection from the modified Data Layer.
    cat=yaml.safe_load((root/'authoring/pattern_instance_catalog.yaml').read_text()) or {}
    cat['instances']=[x for x in cat.get('instances',[]) if x.get('artifact_id')!='A_GENERATED_PLAYBOOK_PACKAGE']
    (root/'authoring/pattern_instance_catalog.yaml').write_text(yaml.safe_dump(cat,sort_keys=False))
    cp_x=subprocess.run([sys.executable,str(R/'tools/materialize_pattern_data_layer_expansion.py'),str(root)],capture_output=True,text=True)
    ck(cp_x.returncode==0,'failed to rematerialize one-instance Data-Layer expansion: '+cp_x.stdout+cp_x.stderr)
    cp_d=subprocess.run([sys.executable,str(R/'tools/derive_pattern_execution_projection.py'),str(root)],capture_output=True,text=True)
    ck(cp_d.returncode==0,'failed to rederive one-instance projection: '+cp_d.stdout+cp_d.stderr)
    # Realize the remaining projected components; the removed package pattern remains only a +50 opportunity.
    proj=yaml.safe_load((root/'authoring/pattern_execution_projection.yaml').read_text()) or {}; comp={}; outgoing={}; incoming={}
    for f in proj.get('fragments',[]):
        for c in f.get('components',[]): comp[c['component_id']]=c
        for e in f.get('edges',[]): outgoing.setdefault(e['from'],[]).append(e['to']); incoming.setdefault(e['to'],[]).append(e['from'])
    nodes=[]; gates=[]
    for cid,c in comp.items():
        if c['kind']=='node':
            n={'id':cid,'question':'pattern role '+c['role'],'answer_type':'structured_record','allowed_from':incoming.get(cid,[])}
            if outgoing.get(cid): n['on_answer']={'update_state':{},'next':outgoing[cid][0]}
            nodes.append(n)
        else: gates.append({'id':cid,'method':'mechanical','trust_class':'deterministic','condition':'true','on_pass':outgoing.get(cid,['END'])[0],'on_fail':'STOP','allowed_from':incoming.get(cid,[])})
    (root/'source/program.ordo.yaml').write_text(yaml.safe_dump({'nodes':nodes,'gates':gates},sort_keys=False))
    cp,o=run({'open_questions':[],'prefilled_confirmations':[],'distinct_variables':[],'pattern_reuse_candidate_root':str(root)})
    ck(cp.returncode==0,'scorer failed on missed reward opportunity: '+cp.stderr)
    if o:
        ck(o.get('process_rewards',{}).get('qualified_reusable_pattern')==50,'only bound + realized reuse should reward 50')
        ck(o['process_score']==1050,'missed opportunity must not penalize; one qualified reuse gives 1050')
        opp=o.get('consolidated_improvement_opportunities',[])
        ck(any(x.get('pattern_id')=='PRODUCTION_PACKAGE_MATERIALIZATION' and x.get('potential_points')==50 for x in opp),'missed +50 reward opportunity not surfaced to optimizer')

# Duplicate capability signal for same artifact/pattern cannot double reward because semantic opportunity is deduplicated.
ev=subprocess.run([sys.executable,str(R/'tools/evaluate_pattern_reuse_opportunities.py'),str(R)],capture_output=True,text=True)
ck(ev.returncode==0,'reuse evaluator failed')
if ev.returncode==0:
    er=json.loads(ev.stdout); sids=[x['semantic_responsibility_id'] for x in er['qualified_reuse_events']]
    ck(len(sids)==len(set(sids)),'deterministic evaluator produced duplicate semantic reward units')

print(json.dumps({'status':'PASS' if not fail else 'FAIL','passed':passed,'failed':len(fail),'failures':fail},indent=2))
sys.exit(1 if fail else 0)
