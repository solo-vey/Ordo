#!/usr/bin/env python3
import argparse, json, zipfile, hashlib, pathlib, re, sys

def sha256(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def load_run(z):
 with zipfile.ZipFile(z) as a:
  r=json.loads(a.read('RUN_REPORT.json')); d=json.loads(a.read('DRIVER_RECEIPTS.json')); t=json.loads(a.read('TERMINAL_PROOF.json'))
 return r,d,t

def score(r,d,t):
 process=100
 if not d.get('complete'): process-=35
 if not d.get('version_bound'): process-=20
 if not t.get('match'): process-=50
 if r.get('manual_mutation'): process-=50
 if r.get('cross_artifact_fidelity')!='PASS': process-=35
 if r.get('status')!='PASS': process-=35
 # Evidence-only campaign has no generated canonical docs in archive; score document evidence quality, not blind document quality.
 document=100
 if r.get('cross_artifact_fidelity')!='PASS': document-=45
 if not r.get('driver_receipts_complete'): document-=25
 if not r.get('events'): document-=20
 if r.get('expected_outcome','').startswith('PASS') and not r.get('approvals_complete'): document-=30
 final=round((process+document)/2)
 return max(0,process),max(0,document),max(0,final)

def evaluate(args):
 policy=json.load(open(args.policy)); out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
 runs=[]; candidate=None; zero=[]
 for z in sorted(pathlib.Path(args.evidence_dir).glob('RUN_*_PRE_RELEASE_EVIDENCE.zip')):
  r,d,t=load_run(z); candidate=candidate or r['sealed_candidate_sha256']
  p,doc,fin=score(r,d,t)
  trace=[{'seq':e.get('seq'),'event':e.get('event'),'decision_evidence':{k:v for k,v in e.items() if k not in ('seq','event')}} for e in r.get('events',[])]
  defects=[]
  if r.get('manual_mutation'): defects.append('manual_mutation')
  if not t.get('match'): defects.append('terminal_mismatch')
  if not d.get('complete'): defects.append('incomplete_driver_receipts')
  if r.get('cross_artifact_fidelity')!='PASS': defects.append('cross_artifact_fidelity_failure')
  zero += defects
  rec={'run_id':r['run_id'],'labels':policy['evidence_labels'],'process_quality':p,'document_quality':doc,'final_quality':fin,'terminal_state_correct':bool(t.get('match')),'driver_receipts_complete':bool(d.get('complete')),'selected_route_trace':trace,'correction_loop_used':bool(r.get('correction_loop_used')),'zero_tolerance_defects':defects,'limitations':['Deterministic harness evidence; no independent external LLM execution.','Document score reflects packaged validation evidence because canonical generated documents are not embedded in this evidence ZIP.']}
  runs.append(rec); (out/f"{r['run_id']}_INTERNAL_EVALUATION.json").write_text(json.dumps(rec,indent=2,ensure_ascii=False)+'\n')
 avg=round(sum(x['final_quality'] for x in runs)/len(runs),2)
 th=policy['thresholds']; passed=not zero and all(x['process_quality']>=th['min_process_per_run'] and x['document_quality']>=th['min_document_per_run'] and x['final_quality']>=th['min_final_per_run'] for x in runs) and avg>=th['min_campaign_average']
 report={'schema_version':'ordo.internal_dry_evaluation_campaign.v1','candidate_sha256':candidate,'evidence_class':'INTERNAL_DRY_EVALUATION','blindness':'NOT_BLIND','canonical_status':'NOT_CANONICAL_BENCHMARK_EVIDENCE','runs':runs,'campaign_average':avg,'thresholds':th,'threshold_result':'PASS' if passed else 'FAIL','zero_tolerance_defects':sorted(set(zero)),'promotion_status':'BLOCKED_AWAITING_USER_ACCEPTANCE' if passed else 'BLOCKED_THRESHOLD_FAILURE','required_user_decision':policy['allowed_decisions']}
 (out/'INTERNAL_DRY_EVALUATION_CAMPAIGN_REPORT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 md=['# Internal dry evaluation','',f"Candidate: `{candidate}`",f"Threshold result: **{report['threshold_result']}**",f"Promotion: **{report['promotion_status']}**",'', '| RUN | Process | Documents | Final | Terminal |','|---|---:|---:|---:|---|']
 for x in runs: md.append(f"| {x['run_id']} | {x['process_quality']} | {x['document_quality']} | {x['final_quality']} | {'PASS' if x['terminal_state_correct'] else 'FAIL'} |")
 md += ['',f"Campaign average: **{avg}**",'', 'External blind testing remains blocked until an explicit acceptance receipt is recorded.']
 (out/'INTERNAL_DRY_EVALUATION_SUMMARY.md').write_text('\n'.join(md)+'\n')
 print(json.dumps({'status':'PASS','report':str(out/'INTERNAL_DRY_EVALUATION_CAMPAIGN_REPORT.json'),'promotion_status':report['promotion_status']})); return 0

def accept(args):
 report=json.load(open(args.report)); decision=args.decision
 if decision not in ('ACCEPT_FOR_EXTERNAL_BLIND_TESTING','REJECT_AND_IMPROVE','ACCEPT_WITH_RECORDED_RISK','PAUSE_FOR_OWNER_INPUT'): raise SystemExit('invalid decision')
 if decision=='ACCEPT_FOR_EXTERNAL_BLIND_TESTING' and report['threshold_result']!='PASS': raise SystemExit('threshold failure requires ACCEPT_WITH_RECORDED_RISK or rejection')
 if decision=='ACCEPT_WITH_RECORDED_RISK' and not args.rationale: raise SystemExit('rationale required')
 receipt={'schema_version':'ordo.internal_dry_user_acceptance.v1','candidate_sha256':report['candidate_sha256'],'decision':decision,'user_confirmed':True,'rationale':args.rationale or '', 'risk_acknowledged':decision=='ACCEPT_WITH_RECORDED_RISK'}
 pathlib.Path(args.out).write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n'); print(json.dumps({'status':'RECORDED','decision':decision})); return 0

def promote(args):
 report=json.load(open(args.report)); receipt=json.load(open(args.receipt)); out=pathlib.Path(args.out)
 if receipt.get('candidate_sha256')!=report.get('candidate_sha256'): raise SystemExit('candidate hash mismatch')
 if receipt.get('decision') not in ('ACCEPT_FOR_EXTERNAL_BLIND_TESTING','ACCEPT_WITH_RECORDED_RISK'): raise SystemExit('promotion blocked by user decision')
 out.mkdir(parents=True,exist_ok=True)
 # Leakage-safe neutral prompts.
 for i in range(1,6): (out/f'RUN_{i:02d}_NEUTRAL_PROMPT.md').write_text(f"Load the sealed candidate package and execute canonical RUN_{i:02d}. Return only the factual result package or terminal report with integrity evidence.\n")
 shutil=None
 manifest={'schema_version':'ordo.external_blind_handoff.v1','candidate_sha256':report['candidate_sha256'],'acceptance_decision':receipt['decision'],'contains_internal_scores':False,'contains_diagnostic_hints':False,'status':'READY_FOR_EXTERNAL_BLIND_TESTING'}
 (out/'EXTERNAL_BLIND_PROMOTION_REPORT.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps({'status':'READY_FOR_EXTERNAL_BLIND_TESTING','out':str(out)})); return 0

def main():
 p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True)
 e=s.add_parser('evaluate'); e.add_argument('--evidence-dir',required=True); e.add_argument('--policy',required=True); e.add_argument('--out',required=True); e.set_defaults(fn=evaluate)
 a=s.add_parser('accept'); a.add_argument('--report',required=True); a.add_argument('--decision',required=True); a.add_argument('--rationale'); a.add_argument('--out',required=True); a.set_defaults(fn=accept)
 g=s.add_parser('promote'); g.add_argument('--report',required=True); g.add_argument('--receipt',required=True); g.add_argument('--out',required=True); g.set_defaults(fn=promote)
 args=p.parse_args(); return args.fn(args)
if __name__=='__main__': sys.exit(main())
