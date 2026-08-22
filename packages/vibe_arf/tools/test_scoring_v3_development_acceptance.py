from pathlib import Path
import json, subprocess, tempfile, sys
R=Path(__file__).resolve().parents[1]
errors=[]
def ck(c,m):
    if not c: errors.append(m)
q=json.loads((R/'source/quality_acceptance_policy.json').read_text())
a=json.loads((R/'source/autonomous-playbook-improvement-policy.json').read_text())
mp=json.loads((R/'source/model-response-provenance-policy.json').read_text())
ck(q.get('format') in ('vibe-quality-acceptance-policy/v5','vibe-quality-acceptance-policy/v6','vibe-quality-acceptance-policy/v7','vibe-quality-acceptance-policy/v8'),'quality policy is not supported v5-v7')
ck('development_score' in q,'development_score contract missing')
ck('acceptance_score' in q,'acceptance_score contract missing')
ck(q.get('development_score',{}).get('availability')=='always_numeric_for_valid_evaluated_candidate','development score availability wrong')
ck(q.get('acceptance_score',{}).get('availability')=='only_when_live_acceptance_provenance_eligible','acceptance availability wrong')
ck(a.get('quality_evaluation',{}).get('ranking')=='strictly greater development_score wins; ties do not replace best-so-far','optimizer ranking is not development_score')
ck('protected-dimension eligibility first' in a.get('termination',{}).get('best_comparison','') and 'strictly greater development_score' in a.get('termination',{}).get('best_comparison',''),'stagnation not based on protected eligibility + development_score')
ck(mp.get('result_eligibility',{}).get('missing_provenance')=='fail_closed_for_acceptance_only; development scoring remains available with explicit offline_conformance tier','provenance policy still blocks development scoring')
scorer=R/'tools/calculate_playbook_quality_score.py'
base={
 'evidence_tier':'offline_conformance',
 'result_eligibility':{'status':'FAIL','result_scoring_eligible':False},
 'process':{'open_questions':[], 'prefilled_confirmations':[], 'distinct_variables':['v1']},
 'result_documents':[{'id':'d','technical':False,'artifact_lineage_valid_for_development':True,'reference_variants':[{'id':'r','missing_major_parts':0,'missing_or_incomplete_details':2}]}]
}
with tempfile.TemporaryDirectory() as td:
    p=Path(td); i=p/'in.json'; o=p/'out.json'; i.write_text(json.dumps(base))
    cp=subprocess.run([sys.executable,str(scorer),str(i),str(o)],capture_output=True,text=True)
    ck(cp.returncode==0,'offline development scoring failed: '+cp.stderr)
    if o.exists():
        x=json.loads(o.read_text())
        ck(x.get('status')=='PASS','offline score status not PASS')
        ck(x.get('evidence_tier')=='offline_conformance','evidence tier missing')
        ck(isinstance(x.get('development_score'),(int,float)),'development_score not numeric')
        ck(x.get('acceptance_score') is None,'acceptance_score must be null offline')
        ck(x.get('acceptance_status')=='UNAVAILABLE_PROVENANCE_INELIGIBLE','acceptance status wrong offline')
    live=json.loads(json.dumps(base)); live['evidence_tier']='live_acceptance'; live['result_eligibility']={'status':'PASS','result_scoring_eligible':True}
    i.write_text(json.dumps(live)); cp=subprocess.run([sys.executable,str(scorer),str(i),str(o)],capture_output=True,text=True)
    ck(cp.returncode==0,'live scoring failed: '+cp.stderr)
    if o.exists():
        x=json.loads(o.read_text())
        ck(isinstance(x.get('development_score'),(int,float)),'live development score missing')
        ck(isinstance(x.get('acceptance_score'),(int,float)),'live acceptance score missing')
        ck(x.get('acceptance_status')=='AVAILABLE','live acceptance status wrong')
        ck(abs(float(x['development_score'])-float(x['acceptance_score']))<1e-9,'live development/acceptance mismatch on same evidence')
if errors:
    print('SCORING V3: FAIL')
    for e in errors: print('-',e)
    sys.exit(1)
print('SCORING V3: PASS')
