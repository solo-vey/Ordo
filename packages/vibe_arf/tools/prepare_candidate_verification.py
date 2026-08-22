#!/usr/bin/env python3
from pathlib import Path
import argparse, json, hashlib, time, sys

def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def timing_map(root):
    merged={}
    baseline=root/'verification/CANDIDATE_TIMING_BASELINE.json'
    if baseline.is_file():
        try:
            bd=load(baseline)
            for k,v in (bd.get('checks') or {}).items(): merged[str(k)]=float(v)
        except Exception: pass
    candidates=sorted((root/'reports').glob('CANDIDATE_SHARD_*.json'), reverse=True)+[root/'reports/VERIFICATION_EVIDENCE_SUMMARY.json']+sorted((root/'reports').glob('*PRE_EDITOR*.json'), reverse=True)
    for p in candidates:
        try:
            d=load(p)
            for r in d.get('checks') or []:
                if r.get('id') and r.get('elapsed_s') is not None:
                    merged.setdefault(r['id'],float(r.get('elapsed_s') or 0.5))
        except Exception: pass
    return merged

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); ap.add_argument('--output',default='reports/CANDIDATE_VERIFICATION_PLAN.json'); ap.add_argument('--target-seconds',type=float,default=8.0); ap.add_argument('--operational-limit-seconds',type=float,default=20.0)
    a=ap.parse_args(); root=Path(a.package).resolve(); prof=load(root/'verification_profile.json'); tm=timing_map(root)
    sys.path.insert(0,str(root/'tools')); from verification_package_fingerprint import package_fingerprint
    package_fp=package_fingerprint(root)
    phase_order=['FAST','PRE_EDITOR','POST_EDITOR','RELEASE']
    cutoff=phase_order.index('PRE_EDITOR')
    checks=[c for c in prof['checks'] if phase_order.index(c.get('phase'))<=cutoff]
    shards=[]; cur=[]; est=0.0; prior=[]
    for c in checks:
        if c['id'] in tm:
            ce=max(0.05,tm[c['id']])
        else:
            runner_default_seconds={'trusted_python_regression':5.0,'python_script':1.0}.get(c.get('runner'),0.75)
            ce=max(0.05,runner_default_seconds)
        # Never place a known expensive check behind an already sizeable shard.
        if cur and est+ce>a.target_seconds:
            shards.append((cur,est,list(prior))); prior.extend(x['id'] for x in cur); cur=[]; est=0.0
        cur.append(c); est+=ce
    if cur: shards.append((cur,est,list(prior)))
    out=[]
    for i,(rows,e,prior_ids) in enumerate(shards,1):
        out.append({'index':i,'check_ids':[x['id'] for x in rows],'checkpoint_satisfied':prior_ids,'estimated_seconds':round(e,3),'hard_timeout_seconds':min(float(a.operational_limit_seconds),max(5.0,round(e*2.0+3.0,1))),'report':f'reports/CANDIDATE_SHARD_{i}.json','stdout':f'reports/CANDIDATE_SHARD_{i}.stdout.log','stderr':f'reports/CANDIDATE_SHARD_{i}.stderr.log','status_file':f'reports/CANDIDATE_SHARD_{i}.status.json'})
    payload={'schema_version':'1.0','created_at_epoch':time.time(),'package':str(root),'profile_sha256':sha(root/'verification_profile.json'),'package_fingerprint':package_fp,'checks_total_expected':len(checks),'target_seconds':a.target_seconds,'operational_limit_seconds':a.operational_limit_seconds,'shards':out}
    op=Path(a.output); op=op if op.is_absolute() else root/op; op.parent.mkdir(parents=True,exist_ok=True); op.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({'status':'PASS','plan':str(op),'shards':len(out),'max_estimated_seconds':max((x['estimated_seconds'] for x in out),default=0),'checks_total':len(checks)},indent=2))
    return 0
if __name__=='__main__': raise SystemExit(main())
