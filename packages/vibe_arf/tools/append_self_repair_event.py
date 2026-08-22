#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse,datetime,hashlib,json

def canonical(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--repair-id',required=True); ap.add_argument('--problem',required=True); ap.add_argument('--root-cause',required=True); ap.add_argument('--files-changed',required=True); ap.add_argument('--repair',required=True); ap.add_argument('--validation',required=True); ap.add_argument('--continuation-point',required=True); ap.add_argument('--log-path',default='runtime/evidence/SELF_REPAIR_LOG.jsonl')
    a=ap.parse_args(); root=Path(a.root).resolve(); p=root/a.log_path; p.parent.mkdir(parents=True,exist_ok=True)
    prev=None
    if p.is_file():
        lines=[x for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
        if lines:
            prev=json.loads(lines[-1]).get('entry_sha256')
    rec={'repair_id':a.repair_id,'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'problem':a.problem,'root_cause':a.root_cause,'files_changed':[x.strip() for x in a.files_changed.split(',') if x.strip()],'repair':a.repair,'validation':a.validation,'continuation_point':a.continuation_point,'previous_entry_sha256':prev}
    rec['entry_sha256']=hashlib.sha256(canonical(rec)).hexdigest()
    with p.open('a',encoding='utf-8') as f: f.write(json.dumps(rec,ensure_ascii=False)+'\n')
    print(json.dumps(rec,ensure_ascii=False)); return 0
if __name__=='__main__': raise SystemExit(main())
