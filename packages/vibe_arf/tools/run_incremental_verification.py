#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, fnmatch, tempfile, subprocess, sys, time, os, shlex

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def loadj(p): return json.loads(Path(p).read_text())
def ignored(rel,globs): return any(fnmatch.fnmatch(rel,g) for g in globs)
def inventory(root,cfg):
    out={}
    for p in sorted(root.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(root).as_posix()
        if ignored(rel,cfg.get('ignore_globs',[])): continue
        out[rel]=sha(p)
    return out

def changed_files(old,new):
    return sorted(k for k in set(old)|set(new) if old.get(k)!=new.get(k))
def matches(path,globs): return any(fnmatch.fnmatch(path,g) for g in globs)

def select(cfg,changed,mode):
    checks=set(cfg['modes'][mode].get('safety_checks',[])); forced=None; reasons=[]
    rank={'PATCH':0,'CHECKPOINT':1,'CANDIDATE':2,'RELEASE':3}
    rules=cfg.get('path_rules',[])
    # Evaluate every changed file independently. If a file matches one or more
    # exclusive rules, generic rules for that same file are suppressed. Other
    # changed files still contribute their own dependency-aware matches.
    for path in changed:
        matched=[r for r in rules if matches(path,r.get('globs',[]))]
        exclusive=[r for r in matched if r.get('exclusive') is True]
        chosen=exclusive if exclusive else matched
        for r in chosen:
            added=sorted(set(r.get('checks',[])))
            checks.update(added)
            reasons.append({'changed_file':path,'rule_globs':r.get('globs',[]),'exclusive':bool(r.get('exclusive')),'checks':added})
            mm=r.get('minimum_mode')
            if mm and rank[mm] > rank[mode]: forced=mm if forced is None or rank[mm]>rank[forced] else forced
    return sorted(checks),forced,reasons

def subset_profile(root, selected, checkpoint_pass):
    prof=loadj(root/'verification_profile.json'); byid={c['id']:c for c in prof['checks']}; sel=set(selected)
    # Include dependencies only when they are not trusted PASS at checkpoint.
    todo=list(sel)
    while todo:
        cid=todo.pop(); c=byid.get(cid)
        if not c: continue
        for dep in c.get('depends_on',[]) or []:
            if dep not in sel and checkpoint_pass.get(dep)!='PASS': sel.add(dep); todo.append(dep)
    rows=[]
    for c in prof['checks']:
        if c['id'] not in sel: continue
        x=json.loads(json.dumps(c))
        x['depends_on']=[d for d in x.get('depends_on',[]) if d in sel]
        rows.append(x)
    return {'schema_version':prof['schema_version'],'profile_id':prof['profile_id']+'.incremental','playbook_revision':prof['playbook_revision'],'checks':rows}

def prepare_full_plan(root):
    cmd=[sys.executable,str(root/'tools/prepare_candidate_verification.py'),str(root)]
    p=subprocess.run(cmd,cwd=root,text=True,capture_output=True,timeout=10)
    plan=root/'reports/CANDIDATE_VERIFICATION_PLAN.json'
    return p.returncode,(loadj(plan) if plan.is_file() else {}),p.stdout,p.stderr

def write_checkpoint(root,path,cfg,old_pass,run_report=None):
    passed=dict(old_pass)
    if run_report:
        passed.update({x['id']:'PASS' for x in run_report.get('checks',[]) if x.get('status')=='PASS'})
    payload={'schema_version':'1.0','created_at_epoch':time.time(),'package_root':str(root),'impact_policy_sha256':sha(root/'verification_impact_map.json'),'files':inventory(root,cfg),'passed_checks':passed}
    Path(path).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); ap.add_argument('--mode',choices=['PATCH','CHECKPOINT','CANDIDATE','RELEASE'],default='PATCH'); ap.add_argument('--checkpoint',default='.dev_checkpoint.json'); ap.add_argument('--dry-select',action='store_true'); ap.add_argument('--report',default='reports/INCREMENTAL_VERIFICATION.json')
    a=ap.parse_args(); start=time.time(); root=Path(a.package).resolve(); cfg=loadj(root/'verification_impact_map.json')
    cp=Path(a.checkpoint); cp=cp if cp.is_absolute() else root/cp
    checkpoint=loadj(cp) if cp.is_file() else {'files':{},'passed_checks':{}}
    current=inventory(root,cfg); changed=changed_files(checkpoint.get('files',{}),current)
    selected,forced,selection_reasons=select(cfg,changed,a.mode); effective=forced or a.mode
    if cfg['modes'][effective].get('full_pre_editor'): selected=[]
    base={'status':'PASS','requested_mode':a.mode,'effective_mode':effective,'validation_class':cfg['modes'][effective].get('validation_class','FULL' if cfg['modes'][effective].get('full_pre_editor') else 'FAST'),'changed_files':changed,'selected_checks':selected,'selection_reasons':selection_reasons,'checkpoint':str(cp),'budget_seconds':cfg['modes'][effective]['budget_seconds']}
    if a.dry_select:
        base['elapsed_s']=round(time.time()-start,3); print(json.dumps(base,indent=2)); return 0
    run_report=None; rc=0
    if cfg['modes'][effective].get('full_pre_editor'):
        rc,plan,pout,perr=prepare_full_plan(root)
        base['fresh_full_pre_editor']=False
        base['candidate_plan_prepared']=rc==0
        base['candidate_plan']='reports/CANDIDATE_VERIFICATION_PLAN.json'
        base['shards']=[{'index':x['index'],'estimated_seconds':x['estimated_seconds'],'hard_timeout_seconds':x['hard_timeout_seconds'],'checks':len(x['check_ids'])} for x in plan.get('shards',[])]
        base['checks_total_expected']=plan.get('checks_total_expected')
        base['next_action']='run each persisted shard with tools/run_candidate_verification_shard.py, then aggregate_candidate_verification.py'
        base['runner_stdout_tail']=pout[-1000:]; base['runner_stderr_tail']=perr[-500:]
    elif selected:
        trusted=sorted(k for k,v in checkpoint.get('passed_checks',{}).items() if v=='PASS')
        cmd=[sys.executable,str(root/'tools/run_verification_profile.py'),str(root),'--through','PRE_EDITOR','--report','reports/INCREMENTAL_SELECTED_CHECKS.json','--only',','.join(selected),'--checkpoint-satisfied',','.join(trusted)]
        p=subprocess.run(cmd,cwd=root,text=True,capture_output=True); rc=p.returncode
        rp=root/'reports/INCREMENTAL_SELECTED_CHECKS.json'; run_report=loadj(rp) if rp.is_file() else None
        base['runner_stdout_tail']=p.stdout[-2000:]; base['runner_stderr_tail']=p.stderr[-1000:]
    else:
        base['note']='No tracked input changes; checkpoint remains valid.'
    elapsed=time.time()-start; budget=cfg['modes'][effective]['budget_seconds']; base['elapsed_s']=round(elapsed,3); base['within_budget']=elapsed<=budget; base['status']='PASS' if rc==0 else 'FAIL'
    if rc==0 and effective in {'CHECKPOINT','CANDIDATE','RELEASE'}: write_checkpoint(root,cp,cfg,checkpoint.get('passed_checks',{}),run_report)
    rp=root/a.report; rp.parent.mkdir(parents=True,exist_ok=True); rp.write_text(json.dumps(base,indent=2)+'\n')
    print(json.dumps(base,indent=2)); return rc
if __name__=='__main__': raise SystemExit(main())
