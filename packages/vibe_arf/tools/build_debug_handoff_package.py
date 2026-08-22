#!/usr/bin/env python3
from pathlib import Path
import argparse, json, zipfile, hashlib, datetime

def sha(p):
    h=hashlib.sha256();
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--output',default=None)
    a=ap.parse_args(); root=Path(a.root).resolve(); src=root/'debug_handoff'/'working'
    if not (src/'session_manifest.json').exists(): raise SystemExit('debug handoff bundle not initialized')
    expected={
      'DEBUG_RUN_INDEX.json':None,
      'EXECUTION_RECEIPTS.jsonl':root/'runtime/evidence/EXECUTION_RECEIPTS.jsonl',
      'PER_NODE_TELEMETRY.jsonl':root/'runtime/evidence/PER_NODE_TELEMETRY.jsonl',
      'TIMING_SUMMARY.json':root/'reports/TIMING_SUMMARY.json',
      'TOKEN_USAGE_SUMMARY.json':root/'reports/TOKEN_USAGE_SUMMARY.json',
      'FILE_ACCESS_SUMMARY.json':root/'reports/FILE_ACCESS_SUMMARY.json',
      'SELF_REPAIR_LOG.jsonl':root/'runtime/evidence/SELF_REPAIR_LOG.jsonl',
      'VALIDATION_SUMMARY.json':root/'reports/VALIDATION_SUMMARY.json',
    }
    idx={'schema_version':'1.0','policy':'source/observability-debug-policy.json','surfaces':{}}
    payload=[]
    for name,p in expected.items():
        if p is None: continue
        if p.is_file():
            arc='debug_handoff/working/evidence/'+name; payload.append((arc,p.read_bytes())); idx['surfaces'][name]={'status':'PRESENT','source':str(p.relative_to(root)),'sha256':sha(p)}
        else: idx['surfaces'][name]={'status':'UNAVAILABLE','reason':'not_observable_or_not_materialized_for_this_run'}
    idx['surfaces']['DEBUG_RUN_INDEX.json']={'status':'PRESENT','source':'debug_handoff/working/DEBUG_RUN_INDEX.json'}
    (src/'DEBUG_RUN_INDEX.json').write_text(json.dumps(idx,indent=2,ensure_ascii=False)+'\n')
    out=Path(a.output).resolve() if a.output else root/'debug_handoff'/f"HANDOFF_{datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}.zip"
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(src.parent))
        existing={i.filename for i in z.infolist()}
        for arc,data in payload:
            if arc not in existing: z.writestr(arc,data)
    ev={'package':str(out),'sha256':sha(out),'source':'debug_handoff/working','debug_run_index':'debug_handoff/working/DEBUG_RUN_INDEX.json'}
    (out.with_suffix(out.suffix+'.json')).write_text(json.dumps(ev,indent=2)+'\n')
    print(json.dumps(ev,indent=2))
if __name__=='__main__': main()
