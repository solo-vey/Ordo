#!/usr/bin/env python3
from pathlib import Path
import argparse,json,subprocess,sys,time,os,signal,hashlib

def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); ap.add_argument('--plan',default='reports/CANDIDATE_VERIFICATION_PLAN.json'); ap.add_argument('--shard',type=int,required=True)
    a=ap.parse_args(); root=Path(a.package).resolve(); pp=Path(a.plan); pp=pp if pp.is_absolute() else root/pp; plan=load(pp)
    sys.path.insert(0,str(root/'tools')); from verification_package_fingerprint import package_fingerprint
    if plan.get('profile_sha256')!=sha(root/'verification_profile.json'):
        print(json.dumps({'status':'FAIL','code':'PLAN_PROFILE_STALE'},indent=2)); return 2
    current_fp=package_fingerprint(root)
    if plan.get('package_fingerprint')!=current_fp:
        print(json.dumps({'status':'FAIL','code':'PLAN_PACKAGE_STALE','planned':plan.get('package_fingerprint'),'current':current_fp},indent=2)); return 2
    match=[x for x in plan['shards'] if int(x['index'])==a.shard]
    if not match: print(json.dumps({'status':'FAIL','code':'SHARD_UNKNOWN'},indent=2)); return 2
    sp=match[0]; report=root/sp['report']; stdout_path=root/sp['stdout']; stderr_path=root/sp['stderr']; status_path=root/sp['status_file']; stdout_path.parent.mkdir(parents=True,exist_ok=True)
    cmd=[sys.executable,str(root/'tools/run_verification_profile.py'),str(root),'--through','PRE_EDITOR','--report',sp['report'],'--only',','.join(sp['check_ids']),'--checkpoint-satisfied',','.join(sp.get('checkpoint_satisfied') or [])]
    start=time.time(); rc=124; timed_out=False
    with stdout_path.open('w',encoding='utf-8') as so, stderr_path.open('w',encoding='utf-8') as se:
        p=subprocess.Popen(cmd,cwd=root,stdout=so,stderr=se,start_new_session=True,close_fds=True,env={**os.environ,'OAI_IS_JUPYTER_KERNEL':'0'})
        deadline=start+float(sp['hard_timeout_seconds'])
        expected_ids=list(sp['check_ids'])
        completed_from_report=False
        while True:
            polled=p.poll()
            if polled is not None:
                rc=polled; break
            if report.is_file() and report.stat().st_mtime >= start:
                try:
                    rr=load(report)
                    got=[r.get('id') for r in (rr.get('checks') or [])]
                    if got==expected_ids and rr.get('status') in {'PASS','FAIL'}:
                        completed_from_report=True
                        rc=0 if rr.get('status')=='PASS' else 1
                        try: os.killpg(p.pid,signal.SIGTERM)
                        except ProcessLookupError: pass
                        try: p.wait(timeout=1.0)
                        except subprocess.TimeoutExpired:
                            try: os.killpg(p.pid,signal.SIGKILL)
                            except ProcessLookupError: pass
                        break
                except Exception:
                    pass
            if time.time() >= deadline:
                timed_out=True; rc=124
                try: os.killpg(p.pid,signal.SIGTERM)
                except ProcessLookupError: pass
                try: p.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    try: os.killpg(p.pid,signal.SIGKILL)
                    except ProcessLookupError: pass
                break
            time.sleep(0.2)
    elapsed=round(time.time()-start,3)
    rep=load(report) if report.is_file() else {}
    status={'schema_version':'1.0','shard':a.shard,'status':'PASS' if rc==0 and rep.get('status')=='PASS' else 'FAIL','returncode':rc,'timed_out':timed_out,'elapsed_s':elapsed,'hard_timeout_seconds':sp['hard_timeout_seconds'],'check_ids':sp['check_ids'],'report':sp['report'],'profile_sha256':plan['profile_sha256'],'stdout_path':sp['stdout'],'stderr_path':sp['stderr']}
    status_path.write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps(status,indent=2)); return 0 if status['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
