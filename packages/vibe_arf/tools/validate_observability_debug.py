#!/usr/bin/env python3
from pathlib import Path
import argparse,json,hashlib

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); a=ap.parse_args(); r=Path(a.root).resolve(); errs=[]
 p=r/'source/observability-debug-policy.json'
 if not p.exists(): errs.append('POLICY_MISSING')
 else:
  d=json.loads(p.read_text());
  if d.get('scope')!='cross_domain': errs.append('SCOPE')
  if d.get('pass_count_diagnostic',{}).get('score_effect')!=0: errs.append('PASS_DIAG_SCORE')
  if d.get('context_accounting',{}).get('platform_overhead_separate') is not True: errs.append('OVERHEAD_SEPARATION')
 lp=r/'runtime/evidence/EXECUTION_RECEIPTS.jsonl'
 if lp.exists():
  prev=None
  for i,line in enumerate(lp.read_text().splitlines(),1):
   x=json.loads(line); got=x.get('receipt_sha256'); base=dict(x); base.pop('receipt_sha256',None); exp=hashlib.sha256(json.dumps(base,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
   if got!=exp: errs.append(f'RECEIPT_HASH:{i}')
   if x.get('previous_receipt_sha256')!=prev: errs.append(f'RECEIPT_CHAIN:{i}')
   if x.get('sequence')!=i: errs.append(f'RECEIPT_SEQUENCE:{i}')
   prev=got
 print(json.dumps({'status':'PASS' if not errs else 'FAIL','errors':errs},indent=2)); raise SystemExit(1 if errs else 0)
if __name__=='__main__': main()
