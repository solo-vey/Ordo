#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json, os, signal, subprocess, sys, time, uuid
from pathlib import Path

def _utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def _tail(x,n=3000):
    return (x or '')[-n:]

def run_command(command, *, timeout_seconds=60, long_running_reason=None, cwd=None, env=None, ledger=None, operation_id=None, retry_count=0):
    timeout_seconds=int(timeout_seconds)
    if timeout_seconds>60 and not str(long_running_reason or '').strip():
        return {'status':'FAIL','code':'LONG_RUNNING_REASON_REQUIRED','timeout_seconds':timeout_seconds,'command':list(command)}, 2
    run_id=str(uuid.uuid4()); started=_utc(); t0=time.monotonic()
    kwargs={'cwd':cwd,'env':env,'text':True,'stdout':subprocess.PIPE,'stderr':subprocess.PIPE}
    if os.name=='posix': kwargs['preexec_fn']=os.setsid
    else: kwargs['creationflags']=getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0)
    p=subprocess.Popen(list(command),**kwargs)
    timed_out=False
    try:
        out,err=p.communicate(timeout=timeout_seconds)
        rc=int(p.returncode or 0)
        status='PASS' if rc==0 else 'FAIL'
    except subprocess.TimeoutExpired:
        timed_out=True
        if os.name=='posix':
            try: os.killpg(os.getpgid(p.pid),signal.SIGTERM)
            except Exception: pass
            try: out,err=p.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                try: os.killpg(os.getpgid(p.pid),signal.SIGKILL)
                except Exception: pass
                out,err=p.communicate()
        else:
            try: p.kill()
            except Exception: pass
            out,err=p.communicate()
        rc=124; status='TIMEOUT'
    finished=_utc(); duration_ms=round((time.monotonic()-t0)*1000,3)
    rec={'schema_version':'1.0','run_id':run_id,'operation_id':operation_id or 'deterministic_tool','command':list(command),'started_at':started,'finished_at':finished,'duration_ms':duration_ms,'timeout_seconds':timeout_seconds,'long_running_reason':long_running_reason,'status':status,'returncode':rc,'retry_count':int(retry_count),'diagnostic_reason':'timeout_process_tree_terminated' if timed_out else None,'stdout_tail':_tail(out),'stderr_tail':_tail(err)}
    if ledger:
        lp=Path(ledger); lp.parent.mkdir(parents=True,exist_ok=True)
        with lp.open('a',encoding='utf-8') as f: f.write(json.dumps(rec,ensure_ascii=False)+'\n')
    return rec,rc

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--timeout',type=int,default=60)
    ap.add_argument('--long-running-reason')
    ap.add_argument('--ledger',default='reports/AUTHORING_EXECUTION_TIMING.jsonl')
    ap.add_argument('--operation-id',default='deterministic_tool')
    ap.add_argument('command',nargs=argparse.REMAINDER)
    a=ap.parse_args(); cmd=a.command
    if cmd and cmd[0]=='--': cmd=cmd[1:]
    if not cmd:
        print(json.dumps({'status':'FAIL','code':'COMMAND_REQUIRED'},indent=2)); return 2
    rec,rc=run_command(cmd,timeout_seconds=a.timeout,long_running_reason=a.long_running_reason,cwd=os.getcwd(),env=os.environ.copy(),ledger=a.ledger,operation_id=a.operation_id)
    print(json.dumps(rec,ensure_ascii=False,indent=2)); return rc
if __name__=='__main__': raise SystemExit(main())
