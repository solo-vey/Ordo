from pathlib import Path
import json, subprocess, tempfile, sys
R=Path(__file__).resolve().parents[1]; errors=[]
def ck(c,m):
    if not c: errors.append(m)
q=json.loads((R/'source/quality_acceptance_policy.json').read_text())
a=json.loads((R/'source/autonomous-playbook-improvement-policy.json').read_text())
hr=q.get('hybrid_reference_fidelity',{})
ck(hr.get('mechanical_component',{}).get('required') is True,'mechanical component missing')
ck(hr.get('analytical_component',{}).get('required') is True,'analytical component missing')
ck(hr.get('penalty_explanation_contract',{}).get('required_fields')==['id','source','points','dimension','candidate_evidence','basis','missing_or_weak','remediation'],'penalty explanation contract missing')
ck(hr.get('consolidated_defects',{}).get('optimizer_input') is True,'defects not optimizer input')
qe=a.get('quality_evaluation',{})
ni=str(qe.get('next_iteration_input','')).lower(); dr=str(qe.get('diagnosis_rule','')).lower()
ck('consolidated' in ni and 'sanitized' in ni and 'defect' in ni and 'remediation' in dr and 'defect' in dr,'optimizer feedback wiring missing')
sc=R/'tools/calculate_playbook_quality_score.py'
base={'evidence_tier':'offline_conformance','result_eligibility':{'status':'FAIL','result_scoring_eligible':False},'process':{'open_questions':[],'prefilled_confirmations':[],'distinct_variables':[]},'result_documents':[{'id':'d','technical':False,'artifact_lineage_valid_for_development':True,'reference_variants':[{'id':'r','missing_major_parts':0,'missing_or_incomplete_details':1,'mechanical_defects':[{'id':'M1','points':10,'dimension':'structure','candidate_evidence':'detail absent','basis':'required reference detail','missing_or_weak':'detail','remediation':'add detail'}],'analytical_defects':[{'id':'A1','points':40,'dimension':'semantic_depth','candidate_evidence':'shallow error handling','reference_evidence':'reference separates timeout/retry/schema','basis':'reference-relative semantic depth','missing_or_weak':'operational states','remediation':'expand error-state model'}]}]}]}
with tempfile.TemporaryDirectory() as td:
 p=Path(td); i=p/'i.json'; o=p/'o.json'; i.write_text(json.dumps(base))
 cp=subprocess.run([sys.executable,str(sc),str(i),str(o)],capture_output=True,text=True)
 ck(cp.returncode==0,'hybrid scorer execution failed: '+cp.stderr)
 if o.exists():
  x=json.loads(o.read_text())
  d=x['documents'][0]['selected']
  ck(d.get('mechanical_score')==990,'mechanical score wrong')
  ck(d.get('analytical_score')==960,'analytical score wrong')
  ck(d.get('score')==950,'combined result score wrong')
  defects=x.get('consolidated_defects') or []
  ck(len(defects)>=2,'consolidated defects missing')
  ck(all(z.get('remediation') for z in defects),'remediation missing')
  ck(set(z.get('source') for z in defects)>={'mechanical','analytical'},'defect provenance missing')
if errors:
 print('HYBRID REFERENCE FIDELITY: FAIL'); [print('-',e) for e in errors]; sys.exit(1)
print('HYBRID REFERENCE FIDELITY: PASS')
