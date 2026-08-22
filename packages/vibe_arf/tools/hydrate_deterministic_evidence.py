#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def file_sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def hydrate(path, expected_sha, allow):
    actual=file_sha(path)
    if actual!=expected_sha: raise ValueError('EVIDENCE_HASH_MISMATCH')
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    updates=data.get('state_updates')
    if not isinstance(updates,dict): raise ValueError('EVIDENCE_STATE_UPDATES_MISSING')
    bad=sorted(set(updates)-set(allow))
    if bad: raise ValueError('EVIDENCE_UPDATE_OUTSIDE_ALLOWLIST:'+','.join(bad))
    selected={k:updates[k] for k in allow if k in updates}
    return {'contract':'state_updates_v1','status':'PASS','report':{'source_sha256':actual,'hydrated_fields':sorted(selected)},'state_updates':selected}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--evidence',required=True); ap.add_argument('--sha256',required=True); ap.add_argument('--allow',action='append',default=[]); ap.add_argument('--output')
    a=ap.parse_args()
    try:
        env=hydrate(a.evidence,a.sha256,a.allow)
        txt=json.dumps(env,ensure_ascii=False,indent=2)
        if a.output: Path(a.output).write_text(txt+'\n',encoding='utf-8')
        else: print(txt)
        return 0
    except Exception as e:
        print(json.dumps({'contract':'state_updates_v1','status':'FAIL','report':{'error':str(e)},'state_updates':{}},ensure_ascii=False,indent=2))
        return 2
if __name__=='__main__': raise SystemExit(main())
