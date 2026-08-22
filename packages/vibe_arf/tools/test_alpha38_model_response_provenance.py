from pathlib import Path
import json,subprocess,tempfile,hashlib,sys
R=Path(__file__).resolve().parents[1]
V=R/'tools/validate_model_response_provenance.py'; S=R/'tools/calculate_playbook_quality_score.py'
h=lambda x: hashlib.sha256(x.encode()).hexdigest()
base={'candidate_sha256':h('candidate'),'expected_or_reference_visible_to_generator':False,'fixture_mutated_after_run_start':False,'model_calls':[{'step_index':1,'element_id':'N_X','origin':'live_model_call','effective_input_sha256':h('in'),'output_sha256':h('out'),'candidate_sha256':h('candidate'),'hidden_reference_visible_to_generator':False,'post_generation_mutation':False,'provider':'test','model':'test-model','runtime_run_id':'r1'}],'final_artifact':{'artifact_path':'generated_outputs/out.md','artifact_sha256':h('artifact'),'producer_node_id':'N_MAT','declared_graph_lineage':True,'post_generation_mutation':False}}
with tempfile.TemporaryDirectory() as td:
 p=Path(td); e=p/'e.json'; r=p/'r.json'; e.write_text(json.dumps(base));
 assert subprocess.run([sys.executable,str(V),str(e),str(r)]).returncode==0
 rep=json.loads(r.read_text()); assert rep['status']=='PASS' and rep['result_scoring_eligible'] is True
 bad=json.loads(json.dumps(base)); bad['model_calls'][0]['origin']='synthetic'; e.write_text(json.dumps(bad)); assert subprocess.run([sys.executable,str(V),str(e),str(r)]).returncode!=0
 score_in={'evidence_tier':'offline_conformance','result_eligibility':{'status':'FAIL','result_scoring_eligible':False},'process':{},'result_documents':[{'id':'x','technical':False,'artifact_lineage_valid_for_development':True,'reference_variants':[{'id':'r','missing_major_parts':0,'missing_or_incomplete_details':0}]}]}
 si=p/'si.json'; so=p/'so.json'; si.write_text(json.dumps(score_in)); assert subprocess.run([sys.executable,str(S),str(si),str(so)]).returncode==0
 scored=json.loads(so.read_text()); assert isinstance(scored.get('development_score'),(int,float)) and scored.get('acceptance_score') is None
print('ALPHA38_MODEL_RESPONSE_PROVENANCE_ANTI_HAPPY_PATH: PASS')
