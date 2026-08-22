#!/usr/bin/env python3
from pathlib import Path
import argparse,json,hashlib,time,sys

def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); ap.add_argument('--plan',default='reports/CANDIDATE_VERIFICATION_PLAN.json'); ap.add_argument('--output',default='reports/VERIFICATION_EVIDENCE_SUMMARY.json')
    a=ap.parse_args(); root=Path(a.package).resolve(); pp=Path(a.plan); pp=pp if pp.is_absolute() else root/pp; plan=load(pp)
    sys.path.insert(0,str(root/'tools')); from verification_package_fingerprint import package_fingerprint
    if plan.get('profile_sha256')!=sha(root/'verification_profile.json'):
        print(json.dumps({'status':'FAIL','code':'PLAN_PROFILE_STALE'},indent=2)); return 2
    current_fp=package_fingerprint(root)
    if plan.get('package_fingerprint')!=current_fp:
        print(json.dumps({'status':'FAIL','code':'PLAN_PACKAGE_STALE','planned':plan.get('package_fingerprint'),'current':current_fp},indent=2)); return 2
    missing_shards=[]; failed=[]; rows=[]; shard_rows=[]
    for sp in plan['shards']:
        stp=root/sp['status_file']; rp=root/sp['report']
        if not stp.is_file() or not rp.is_file(): missing_shards.append(sp['index']); continue
        st=load(stp); rep=load(rp); shard_rows.append(st)
        if st.get('status')!='PASS' or rep.get('status')!='PASS': failed.append(sp['index'])
        rows.extend(rep.get('checks') or [])
    expected=[cid for sp in plan['shards'] for cid in sp['check_ids']]; got=[r.get('id') for r in rows]
    duplicate_checks=sorted({x for x in got if got.count(x)>1}); missing_checks=sorted(set(expected)-set(got)); unexpected_checks=sorted(set(got)-set(expected))
    prof=load(root/'verification_profile.json'); required_invariants=sorted({i for c in prof['checks'] if c.get('phase') in {'PRE_CHAT','PRE_EDITOR'} and c.get('required') for i in c.get('invariants',[])})
    passed_invariants=sorted({i for r in rows if r.get('status')=='PASS' for i in r.get('invariants',[])})
    uncovered=sorted(set(required_invariants)-set(passed_invariants))
    ok=not missing_shards and not failed and not missing_checks and not duplicate_checks and not unexpected_checks and len(rows)==plan['checks_total_expected'] and all(r.get('status')=='PASS' for r in rows) and not uncovered
    payload={'schema_version':'1.2','execution_mode':'persisted_external_shards','status':'PASS' if ok else 'FAIL','created_at_epoch':time.time(),'package':str(root),'profile_sha256':plan['profile_sha256'],'checks_total_expected':plan['checks_total_expected'],'checks_total_executed':len(rows),'checks':rows,'shards':shard_rows,'missing_shards':missing_shards,'failed_shards':failed,'missing_checks':missing_checks,'duplicate_checks':duplicate_checks,'unexpected_checks':unexpected_checks,'required_invariants':required_invariants,'passed_invariants':passed_invariants,'unverified_required_invariants':uncovered,'elapsed_s':round(sum(float(s.get('elapsed_s') or 0) for s in shard_rows),3)}
    op=Path(a.output); op=op if op.is_absolute() else root/op; op.write_text(json.dumps(payload,indent=2)+'\n'); print(json.dumps({'status':payload['status'],'report':str(op),'checks':len(rows),'missing_shards':missing_shards,'failed_shards':failed,'unverified_required_invariants':uncovered},indent=2)); return 0 if ok else 1
if __name__=='__main__': raise SystemExit(main())
