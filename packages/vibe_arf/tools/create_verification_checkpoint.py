#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, fnmatch, time

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load_map(root): return json.loads((root/'verification_impact_map.json').read_text())
def ignored(rel, globs): return any(fnmatch.fnmatch(rel,g) for g in globs)
def inventory(root, cfg):
    out={}
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root).as_posix()
        if ignored(rel,cfg.get('ignore_globs',[])): continue
        out[rel]=sha(p)
    return out

def passed_checks(root):
    p=root/'reports/VERIFICATION_EVIDENCE_SUMMARY.json'
    if not p.is_file(): return {}
    try: d=json.loads(p.read_text())
    except Exception: return {}
    return {x['id']:'PASS' for x in d.get('checks',[]) if x.get('status')=='PASS'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); ap.add_argument('--output',default='.dev_checkpoint.json')
    a=ap.parse_args(); root=Path(a.package).resolve(); cfg=load_map(root)
    out=Path(a.output); out=out if out.is_absolute() else root/out
    payload={'schema_version':'1.0','created_at_epoch':time.time(),'package_root':str(root),'impact_policy_sha256':sha(root/'verification_impact_map.json'),'files':inventory(root,cfg),'passed_checks':passed_checks(root)}
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','checkpoint':str(out),'files':len(payload['files']),'passed_checks':len(payload['passed_checks'])},indent=2))
if __name__=='__main__': main()
