#!/usr/bin/env python3
from pathlib import Path
import json,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1]; W=R/'tools/run_with_watchdog.py'; checks=[]
def ck(n,v): checks.append((n,bool(v)))
def run(args,limit=10): return subprocess.run([sys.executable,str(W),*args],capture_output=True,text=True,timeout=limit)
with tempfile.TemporaryDirectory() as td:
    led=Path(td)/'ledger.jsonl'
    p=run(['--timeout','60','--ledger',str(led),'--',sys.executable,'-c','print(123)']); d=json.loads(p.stdout); ck('FAST_PASS',p.returncode==0 and d['status']=='PASS')
    ck('LEDGER_WRITTEN',led.is_file() and len(led.read_text().splitlines())==1)
    p=run(['--timeout','61','--ledger',str(led),'--',sys.executable,'-c','print(1)']); d=json.loads(p.stdout); ck('LONG_REASON_REQUIRED',p.returncode!=0 and d.get('code')=='LONG_RUNNING_REASON_REQUIRED')
    p=run(['--timeout','61','--long-running-reason','bounded integration corpus','--ledger',str(led),'--',sys.executable,'-c','print(1)']); d=json.loads(p.stdout); ck('LONG_REASON_ACCEPTED',p.returncode==0 and d['status']=='PASS')
    t=time.time(); p=run(['--timeout','1','--ledger',str(led),'--',sys.executable,'-c','import time; time.sleep(5)'],limit=8); d=json.loads(p.stdout); ck('TIMEOUT_STATUS',p.returncode==124 and d['status']=='TIMEOUT'); ck('TIMEOUT_BOUNDED',time.time()-t<5)
    ck('TIMEOUT_DIAGNOSTIC',d.get('diagnostic_reason')=='timeout_process_tree_terminated')
pol=json.loads((R/'source/authoring-execution-watchdog-policy.json').read_text()); ck('DEFAULT_60',pol['default_timeout_seconds']==60); ck('NO_BLIND_RETRY',pol['blind_identical_retry_forbidden'] is True); ck('DEGRADATION_DIAGNOSTIC',pol['degradation_diagnostic']['status']=='OPPORTUNITY' and pol['degradation_diagnostic']['score_effect']==0)
failed=[n for n,v in checks if not v]
for n,v in checks: print(('PASS' if v else 'FAIL'),n)
print(f'ALPHA44_AUTHORING_EXECUTION_WATCHDOG: {len(checks)-len(failed)}/{len(checks)} PASS')
raise SystemExit(1 if failed else 0)
