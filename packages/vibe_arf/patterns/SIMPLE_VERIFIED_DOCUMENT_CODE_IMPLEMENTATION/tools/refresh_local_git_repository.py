#!/usr/bin/env python3
import argparse, json, subprocess, sys
from pathlib import Path

def run(repo, *args):
    cp=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True)
    return cp.returncode, cp.stdout.strip(), cp.stderr.strip()

def emit(obj, code=0):
    print(json.dumps(obj,ensure_ascii=False,indent=2))
    raise SystemExit(code)

def main():
    ap=argparse.ArgumentParser(description='Safely refresh a local Git repository using fetch + fast-forward-only semantics.')
    ap.add_argument('--repo',required=True)
    a=ap.parse_args(); repo=Path(a.repo).expanduser().resolve()
    evidence={'repo':str(repo),'commands':[]}
    if not repo.exists() or not repo.is_dir():
        emit({'status':'NOT_APPLICABLE','reason':'not_local_directory','evidence':evidence})
    rc,out,err=run(repo,'rev-parse','--is-inside-work-tree'); evidence['commands'].append({'cmd':'git rev-parse --is-inside-work-tree','rc':rc,'stdout':out,'stderr':err})
    if rc!=0 or out!='true': emit({'status':'NOT_APPLICABLE','reason':'not_git_repository','evidence':evidence})
    rc,root,err=run(repo,'rev-parse','--show-toplevel'); evidence['commands'].append({'cmd':'git rev-parse --show-toplevel','rc':rc,'stdout':root,'stderr':err})
    if rc!=0: emit({'status':'BLOCKED','reason':'git_root_unresolved','evidence':evidence},1)
    repo=Path(root)
    rc,status,err=run(repo,'status','--porcelain'); evidence['commands'].append({'cmd':'git status --porcelain','rc':rc,'stdout':status,'stderr':err})
    if rc!=0: emit({'status':'BLOCKED','reason':'status_failed','evidence':evidence},1)
    if status: emit({'status':'BLOCKED','reason':'dirty_worktree','evidence':evidence},1)
    rc,branch,err=run(repo,'symbolic-ref','--quiet','--short','HEAD'); evidence['commands'].append({'cmd':'git symbolic-ref --quiet --short HEAD','rc':rc,'stdout':branch,'stderr':err})
    if rc!=0 or not branch: emit({'status':'BLOCKED','reason':'detached_head','evidence':evidence},1)
    rc,head,err=run(repo,'rev-parse','HEAD'); evidence['commands'].append({'cmd':'git rev-parse HEAD','rc':rc,'stdout':head,'stderr':err})
    if rc!=0: emit({'status':'BLOCKED','reason':'head_unresolved','branch':branch,'evidence':evidence},1)
    rc,upstream,err=run(repo,'rev-parse','--abbrev-ref','--symbolic-full-name','@{u}'); evidence['commands'].append({'cmd':'git rev-parse --abbrev-ref --symbolic-full-name @{u}','rc':rc,'stdout':upstream,'stderr':err})
    if rc!=0 or not upstream or '/' not in upstream: emit({'status':'BLOCKED','reason':'upstream_missing','branch':branch,'commit':head,'evidence':evidence},1)
    remote=upstream.split('/',1)[0]
    rc,out,err=run(repo,'fetch',remote); evidence['commands'].append({'cmd':f'git fetch {remote}','rc':rc,'stdout':out,'stderr':err})
    if rc!=0: emit({'status':'BLOCKED','reason':'fetch_failed','branch':branch,'commit':head,'upstream':upstream,'evidence':evidence},1)
    rc,counts,err=run(repo,'rev-list','--left-right','--count','HEAD...@{u}'); evidence['commands'].append({'cmd':'git rev-list --left-right --count HEAD...@{u}','rc':rc,'stdout':counts,'stderr':err})
    if rc!=0: emit({'status':'BLOCKED','reason':'ahead_behind_failed','branch':branch,'commit':head,'upstream':upstream,'evidence':evidence},1)
    try: ahead,behind=[int(x) for x in counts.split()]
    except Exception: emit({'status':'BLOCKED','reason':'ahead_behind_unparseable','branch':branch,'commit':head,'upstream':upstream,'evidence':evidence},1)
    if ahead>0 and behind>0:
        emit({'status':'BLOCKED','reason':'diverged','branch':branch,'commit':head,'upstream':upstream,'ahead':ahead,'behind':behind,'evidence':evidence},1)
    if behind>0:
        rc,out,err=run(repo,'merge','--ff-only','@{u}'); evidence['commands'].append({'cmd':'git merge --ff-only @{u}','rc':rc,'stdout':out,'stderr':err})
        if rc!=0: emit({'status':'BLOCKED','reason':'fast_forward_failed','branch':branch,'commit':head,'upstream':upstream,'ahead':ahead,'behind':behind,'evidence':evidence},1)
        rc,newhead,err=run(repo,'rev-parse','HEAD'); evidence['commands'].append({'cmd':'git rev-parse HEAD','rc':rc,'stdout':newhead,'stderr':err})
        rc2,status2,err2=run(repo,'status','--porcelain'); evidence['commands'].append({'cmd':'git status --porcelain','rc':rc2,'stdout':status2,'stderr':err2})
        if rc!=0 or rc2!=0 or status2: emit({'status':'BLOCKED','reason':'post_update_verification_failed','branch':branch,'commit':newhead or head,'upstream':upstream,'evidence':evidence},1)
        emit({'status':'UPDATED','reason':'fast_forwarded','branch':branch,'commit':newhead,'previous_commit':head,'upstream':upstream,'ahead':0,'behind':0,'evidence':evidence})
    emit({'status':'CURRENT','reason':'no_remote_commits_missing','branch':branch,'commit':head,'upstream':upstream,'ahead':ahead,'behind':0,'evidence':evidence})

if __name__=='__main__': main()
