from pathlib import Path
import importlib.util, json, subprocess, sys, tempfile
R=Path(__file__).resolve().parents[1]
fail=[]; passed=0

def ck(c,m):
    global passed
    if c: passed+=1
    else: fail.append(m)

q=json.loads((R/'source/quality_acceptance_policy.json').read_text())
ck(q.get('format')=='vibe-quality-acceptance-policy/v8','quality policy must advance to v8 anti-gaming contract')
ps=q.get('process_score',{}); pen=ps.get('penalties',{}); cc=ps.get('counting_contract',{}); rc=ps.get('reward_contract',{})
ck('distinct_variable' not in pen or pen.get('distinct_variable') in (0,None),'useful distinct variables must not be penalized')
ck(pen.get('redundant_variable')==10,'redundant variable penalty must be 10')
ck(pen.get('redundant_variable_cap')==100,'redundant variable cap must be 100')
ck(pen.get('unsupported_inference')==100,'unsupported inference penalty must be 100')
ck(pen.get('unsupported_inference_cap')==300,'unsupported inference cap must be 300')
ck(ps.get('hard_invalidations',{}).get('unsupported_human_authority_value')=='HARD_INELIGIBLE_SCORE_VISIBLE','unsupported human-authority value must be score-visible HARD_INELIGIBLE')
ck('suppresses' in str(cc.get('interaction_penalty_stacking','')).lower(),'interaction stacking contract must define suppression')
ck(rc.get('qualified_reusable_pattern',{}).get('max_score_contribution')==200,'reusable-pattern reward contribution must be capped at 200')
ck(rc.get('qualified_reusable_pattern',{}).get('points')==50,'each qualified reuse must remain +50 before cap')
ck('E60_QUALITY_INCENTIVE_ANTI_GAMING' in (R/'PLAYBOOK_LAWS.md').read_text(),'E60 anti-gaming law missing')

scorer=R/'tools/calculate_playbook_quality_score.py'
base_doc={'id':'d','technical':False,'artifact_lineage_valid_for_development':True,'reference_variants':[{'id':'r','missing_major_parts':0,'missing_or_incomplete_details':0}]}
def run(proc):
    fixture={'evidence_tier':'offline_conformance','result_eligibility':{'status':'FAIL','result_scoring_eligible':False},'process':proc,'result_documents':[base_doc]}
    with tempfile.TemporaryDirectory() as td:
        i=Path(td)/'in.json'; o=Path(td)/'out.json'; i.write_text(json.dumps(fixture))
        cp=subprocess.run([sys.executable,str(scorer),str(i),str(o)],capture_output=True,text=True)
        return cp, json.loads(o.read_text()) if o.exists() else None

# Useful variables are free; only mechanically evidenced redundancy is penalized.
cp,o=run({'open_questions':[],'prefilled_confirmations':[],'distinct_variables':[f'v{i}' for i in range(25)]})
ck(cp.returncode==0,'scorer failed useful-variable fixture')
if o:
    ck(o['process_penalties'].get('distinct_variable',0)==0,'useful distinct variables still penalized')
    ck(o['process_penalties'].get('redundant_variable',0)==0,'useful variables incorrectly marked redundant')
    ck(o['process_score']==1000,'useful variables should not lower process score')

redundant=[
 {'variable_id':'v_dup','reason':'duplicate_semantic_alias','mechanically_verified':True,'candidate_evidence':'same producer/consumers/value contract as v1'},
 {'variable_id':'v_dead','reason':'unconsumed','mechanically_verified':True,'candidate_evidence':'no consumers'},
 {'variable_id':'v_elim','reason':'constructively_eliminable','mechanically_verified':True,'candidate_evidence':'pure alias transform'}]
cp,o=run({'open_questions':[],'prefilled_confirmations':[],'distinct_variables':['v1','v_dup','v_dead','v_elim'],'redundant_variables':redundant})
ck(cp.returncode==0,'scorer failed redundant-variable fixture')
if o:
    ck(o['process_penalties'].get('redundant_variable')==30,'three proven redundant variables must cost 30')
    ck(o['process_score']==970,'redundant-variable process score mismatch')
    ck(any(x.get('dimension')=='data_layer_economy' and x.get('remediation') for x in o.get('consolidated_defects',[])),'redundant-variable remediation must reach consolidated defects')

# Unsupported non-authority inference is expensive but scoreable.
unsupported=[
 {'id':'u1','field_id':'I_X','authority_class':'derivable_with_evidence','mechanically_verified':True,'candidate_evidence':'value used with no source/provenance'},
 {'id':'u2','field_id':'I_Y','authority_class':'derivable_with_evidence','mechanically_verified':True,'candidate_evidence':'value used with no source/provenance'}]
cp,o=run({'open_questions':[],'prefilled_confirmations':[],'unsupported_inferences':unsupported})
ck(cp.returncode==0,'ordinary unsupported inference should remain scoreable')
if o:
    ck(o['process_penalties'].get('unsupported_inference')==200,'two unsupported inferences must cost 200')
    ck(o['process_score']==800,'unsupported-inference process score mismatch')
    ck(any(x.get('dimension')=='evidence_integrity' and x.get('remediation') for x in o.get('consolidated_defects',[])),'unsupported-inference remediation must reach consolidated defects')

# Human-authority fabrication remains diagnosable but can never be accepted or replace best-so-far.
cp,o=run({'open_questions':[],'prefilled_confirmations':[],'unsupported_inferences':[{'id':'ua','field_id':'I_ACCEPT','authority_class':'human_authority','mechanically_verified':True,'candidate_evidence':'model assigned approval without analyst evidence'}]})
ck(cp.returncode==0,'HARD_INELIGIBLE revision must retain score visibility')
if o:
    ck(o.get('revision_eligibility_state')=='HARD_INELIGIBLE','authority violation must be HARD_INELIGIBLE')
    ck(o.get('hard_violation_count')==1,'authority hard violation count mismatch')
    ck(any(x.get('id')=='UNSUPPORTED_HUMAN_AUTHORITY_VALUE' for x in o.get('hard_invalidations',[])),'authority invalidation evidence missing')

# Same interaction: group-collapse is the dominant scope defect and suppresses cross-group duplicate penalty.
proc={'open_questions':[{'id':'q1','parameter_ids':['a','b','c'],'groups':['A','B','C']}], 'prefilled_confirmations':[], 'group_collapse_interactions':[{'interaction_id':'q1','group_count':3,'mechanically_verified':True,'candidate_evidence':'one prompt collapses three semantic groups'}]}
cp,o=run(proc)
ck(cp.returncode==0,'scorer failed stacking fixture')
if o:
    ck(o['process_penalties'].get('open_question')==30,'base interaction penalty mismatch')
    ck(o['process_penalties'].get('open_question_additional_variable')==20,'additional-variable penalty mismatch')
    ck(o['process_penalties'].get('group_collapse')==300,'group-collapse penalty mismatch')
    ck(o['process_penalties'].get('open_question_cross_group')==0,'cross-group penalty must be suppressed for same collapsed interaction')
    ck(o['process_score']==650,'stacking process score must be 1000-30-20-300')

# Cross-group still applies when group collapse is not independently proven.
cp,o=run({'open_questions':[{'id':'q1','parameter_ids':['a'],'groups':['A','B','C']}], 'prefilled_confirmations':[]})
ck(cp.returncode==0,'scorer failed cross-group-only fixture')
if o:
    ck(o['process_penalties'].get('open_question_cross_group')==120,'three-group open question must retain -120 cross-group penalty without collapse proof')

# Reward calibration helper keeps +50 per event but caps score contribution at +200.
spec=importlib.util.spec_from_file_location('scoremod',scorer); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
ck(hasattr(mod,'calibrate_reuse_reward'),'reward calibration helper missing')
if hasattr(mod,'calibrate_reuse_reward'):
    ck(mod.calibrate_reuse_reward(0)==0,'reward calibration 0 mismatch')
    ck(mod.calibrate_reuse_reward(100)==100,'reward calibration must preserve +100')
    ck(mod.calibrate_reuse_reward(250)==200,'reward contribution must cap at +200')

print(json.dumps({'status':'PASS' if not fail else 'FAIL','passed':passed,'failed':len(fail),'failures':fail},indent=2))
sys.exit(1 if fail else 0)
