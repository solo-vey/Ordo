#!/usr/bin/env python3
from pathlib import Path
import argparse, json, hashlib, datetime

def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--run-id',required=True); ap.add_argument('--from-node',required=True); ap.add_argument('--to-node',required=True); ap.add_argument('--route',required=True); ap.add_argument('--input-sha',required=True); ap.add_argument('--update-sha',required=True); ap.add_argument('--status',required=True)
 a=ap.parse_args(); root=Path(a.root); p=root/'runtime/evidence/EXECUTION_RECEIPTS.jsonl'; p.parent.mkdir(parents=True,exist_ok=True)
 rows=[json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []; prev=rows[-1].get('receipt_sha256') if rows else None
 rec={'run_id':a.run_id,'sequence':len(rows)+1,'from_node':a.from_node,'to_node':a.to_node,'route':a.route,'input_projection_sha256':a.input_sha,'state_update_sha256':a.update_sha,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':a.status,'previous_receipt_sha256':prev}
 rec['receipt_sha256']=hashlib.sha256(canon(rec)).hexdigest()
 with p.open('a',encoding='utf-8') as f: f.write(json.dumps(rec,ensure_ascii=False,sort_keys=True)+'\n')
 print(json.dumps(rec,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
