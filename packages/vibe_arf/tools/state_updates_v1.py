#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
VALID_STATUS={'PASS','PASS_WITH_NOTES','FAIL'}

def validate_envelope(x):
    errs=[]
    if not isinstance(x,dict): return ['result must be object']
    if x.get('contract')!='state_updates_v1': errs.append('contract must be state_updates_v1')
    if x.get('status') not in VALID_STATUS: errs.append('invalid status')
    if not isinstance(x.get('report'),dict): errs.append('report must be object')
    if not isinstance(x.get('state_updates'),dict): errs.append('state_updates must be object')
    return errs

def merge(a,b):
    out=dict(a)
    for k,v in b.items():
        if isinstance(v,dict) and isinstance(out.get(k),dict): out[k]=merge(out[k],v)
        else: out[k]=v
    return out

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True)
    v=sub.add_parser('validate'); v.add_argument('--result',required=True)
    m=sub.add_parser('merge'); m.add_argument('--state',required=True); m.add_argument('--result',required=True); m.add_argument('--output',required=True)
    a=ap.parse_args(); result=json.loads(Path(a.result).read_text(encoding='utf-8')); errs=validate_envelope(result)
    if errs:
        print(json.dumps({'status':'FAIL','errors':errs},indent=2)); return 2
    if a.cmd=='validate': print(json.dumps({'status':'PASS','contract':'state_updates_v1'},indent=2)); return 0
    state=json.loads(Path(a.state).read_text(encoding='utf-8'))
    if not isinstance(state,dict): print(json.dumps({'status':'FAIL','errors':['state must be object']},indent=2)); return 2
    # Only state_updates is mergeable; report is evidence only.
    updates=result['state_updates'] if result['status']!='FAIL' else {}
    merged=merge(state,updates); Path(a.output).write_text(json.dumps(merged,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','merged_keys':sorted(updates)},ensure_ascii=False)); return 0
if __name__=='__main__': raise SystemExit(main())
