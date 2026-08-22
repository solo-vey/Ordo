#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, tempfile, hashlib, sys
R=Path(__file__).resolve().parents[1]
V=R/'tools/validate_model_response_provenance.py'
S=R/'tools/calculate_playbook_quality_score.py'
P=R/'source/pseudo-live-optimization-policy.json'
h=lambda x: hashlib.sha256(x.encode()).hexdigest()

def runv(e):
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); ep=td/'e.json'; rp=td/'r.json'; ep.write_text(json.dumps(e))
        rc=subprocess.run([sys.executable,str(V),str(ep),str(rp)],capture_output=True,text=True)
        rep=json.loads(rp.read_text()) if rp.exists() else {}
        return rc.returncode,rep

assert P.is_file(), 'pseudo-live policy missing'
pol=json.loads(P.read_text())
assert 'PSEUDO_LIVE_OPTIMIZATION' in pol['execution_modes'] and 'LIVE_ACCEPTANCE' in pol['execution_modes']
assert 'PSEUDO_LIVE_SYNTHETIC' in pol['response_origins']

cand=h('candidate'); inp=h('input'); out=h('output'); art=h('artifact')
pseudo={'execution_mode':'PSEUDO_LIVE_OPTIMIZATION','candidate_sha256':cand,'expected_or_reference_visible_to_generator':False,'fixture_mutated_after_run_start':False,
'executed_model_nodes':['N_X'],
'model_calls':[{'step_index':1,'element_id':'N_X','origin':'PSEUDO_LIVE_SYNTHETIC','effective_input_sha256':inp,'response_binding_input_sha256':inp,'output_sha256':out,'candidate_sha256':cand,'hidden_reference_visible_to_generator':False,'post_generation_mutation':False,'generator_policy_version':'pseudo-live/v1','generator_identity':'test-model','generation_config_hash':h('config')}],
'final_artifact':{'artifact_path':'generated_outputs/out.md','artifact_sha256':art,'producer_node_id':'N_MAT','declared_graph_lineage':True,'post_generation_mutation':False}}
rc,rep=runv(pseudo); assert rc==0,rep
assert rep['pseudo_score_eligible'] is True and rep['formal_score_eligible'] is False
assert rep['provenance_tier']=='PSEUDO_LIVE_SYNTHETIC'

bad=json.loads(json.dumps(pseudo)); bad['model_calls'][0]['response_binding_input_sha256']=h('different')
rc,rep=runv(bad); assert rc!=0 and any('input binding' in e for e in rep['errors']),rep

leak=json.loads(json.dumps(pseudo)); leak['model_calls'][0]['hidden_reference_visible_to_generator']=True
rc,rep=runv(leak); assert rc!=0

# A fully deterministic live path is valid with zero model calls.
det={'execution_mode':'LIVE_ACCEPTANCE','candidate_sha256':cand,'expected_or_reference_visible_to_generator':False,'fixture_mutated_after_run_start':False,'executed_model_nodes':[],'model_calls':[],
'final_artifact':{'artifact_path':'generated_outputs/out.md','artifact_sha256':art,'producer_node_id':'N_MAT','declared_graph_lineage':True,'post_generation_mutation':False}}
rc,rep=runv(det); assert rc==0,rep
assert rep['formal_score_eligible'] is True and rep['verified_model_steps']==0

# But a live path that executed a model node cannot use pseudo evidence.
live_bad=json.loads(json.dumps(pseudo)); live_bad['execution_mode']='LIVE_ACCEPTANCE'
rc,rep=runv(live_bad); assert rc!=0 and rep['formal_score_eligible'] is False

# Explicit pseudo score namespace; formal namespace stays null.
with tempfile.TemporaryDirectory() as td:
    td=Path(td); si=td/'i.json'; so=td/'o.json'
    score_in={'evidence_tier':'pseudo_live_optimization','result_eligibility':{'status':'PASS','pseudo_score_eligible':True,'formal_score_eligible':False},'process':{},'result_documents':[{'id':'x','technical':False,'artifact_lineage_valid_for_development':True,'reference_variants':[{'id':'r','missing_major_parts':0,'missing_or_incomplete_details':0}]}]}
    si.write_text(json.dumps(score_in)); rc=subprocess.run([sys.executable,str(S),str(si),str(so)],capture_output=True,text=True)
    assert rc.returncode==0,rc.stderr
    scored=json.loads(so.read_text())
    assert isinstance(scored.get('pseudo_result_score'),(int,float)) and isinstance(scored.get('pseudo_playbook_score'),(int,float))
    assert scored.get('pseudo_score_eligible') is True
    assert scored.get('formal_result_score') is None and scored.get('formal_playbook_score') is None and scored.get('formal_score_eligible') is False
print('ALPHA42_PSEUDO_LIVE_OPTIMIZATION: PASS')
