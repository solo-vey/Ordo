#!/usr/bin/env python3
import pathlib, tempfile, subprocess, json, shutil, sys
root=pathlib.Path(__file__).resolve().parents[1]; tool=root/'tools/manage_internal_dry_evaluation.py'; policy=root/'INTERNAL_DRY_EVALUATION_POLICY.json'; ev=root/'PRE_RELEASE_EXECUTION_EVIDENCE'
res=[]
with tempfile.TemporaryDirectory() as td:
 td=pathlib.Path(td); out=td/'eval'
 p=subprocess.run([sys.executable,str(tool),'evaluate','--evidence-dir',str(ev),'--policy',str(policy),'--out',str(out)],capture_output=True,text=True); res.append(('five_runs_evaluated',p.returncode==0 and len(list(out.glob('RUN_*_INTERNAL_EVALUATION.json')))==5))
 rpt=out/'INTERNAL_DRY_EVALUATION_CAMPAIGN_REPORT.json'; data=json.load(open(rpt)); res.append(('promotion_blocked_without_user',data['promotion_status']=='BLOCKED_AWAITING_USER_ACCEPTANCE'))
 bad=subprocess.run([sys.executable,str(tool),'accept','--report',str(rpt),'--decision','ACCEPT_WITH_RECORDED_RISK','--out',str(td/'r.json')],capture_output=True,text=True); res.append(('risk_requires_rationale',bad.returncode!=0))
 ok=subprocess.run([sys.executable,str(tool),'accept','--report',str(rpt),'--decision','ACCEPT_FOR_EXTERNAL_BLIND_TESTING','--out',str(td/'a.json')],capture_output=True,text=True); res.append(('acceptance_recorded',ok.returncode==0))
 prom=subprocess.run([sys.executable,str(tool),'promote','--report',str(rpt),'--receipt',str(td/'a.json'),'--out',str(td/'bundle')],capture_output=True,text=True); texts=' '.join(p.read_text() for p in (td/'bundle').glob('*.md')); res.append(('neutral_bundle_no_score_leakage',prom.returncode==0 and 'Process Quality' not in texts and 'correction' not in texts.lower()))
report={'schema_version':'ordo.internal_dry_evaluation_acceptance_tests.v1','tests':[{'name':n,'status':'PASS' if v else 'FAIL'} for n,v in res],'passed':sum(v for _,v in res),'total':len(res),'status':'PASS' if all(v for _,v in res) else 'FAIL'}
(root/'reports'/'INTERNAL_DRY_EVALUATION_ACCEPTANCE_TESTS.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report)); sys.exit(0 if all(v for _,v in res) else 1)
