#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PKG_ROOT=ROOT.parents[1]
TESTS=ROOT/'tests'
PY=sys.executable
ENV=os.environ.copy()
ENV['PYTHONPATH']=os.pathsep.join([str(PKG_ROOT),str(ROOT),ENV.get('PYTHONPATH','')])

def stamp(): return dt.datetime.now().astimezone().isoformat(timespec='milliseconds')
def run_stage(name, cmd, cwd=ROOT, timeout=60):
    start=stamp(); t=time.perf_counter(); print(f'[{name}] START {start}',flush=True)
    try:
        cp=subprocess.run(cmd,cwd=cwd,env=ENV,text=True,capture_output=True,timeout=timeout)
        elapsed=time.perf_counter()-t; end=stamp()
        print(f'[{name}] END   {end} elapsed={elapsed:.3f}s rc={cp.returncode}',flush=True)
        if cp.returncode==0:
            if cp.stdout: print(cp.stdout,end='')
        else:
            tail='\n'.join((cp.stdout+'\n'+cp.stderr).splitlines()[-24:])
            if tail: print(tail,file=sys.stderr)
        failed_tests=re.findall(r'^FAILED\s+(\S+)', cp.stdout, flags=re.M)
        failed_js=re.findall(r'^FAILED_JS:(.+)$', cp.stdout, flags=re.M)
        return {'name':name,'start':start,'end':end,'elapsed_s':round(elapsed,3),'rc':cp.returncode,'timeout':False,'failed_tests':failed_tests,'failed_js':failed_js}
    except subprocess.TimeoutExpired as e:
        elapsed=time.perf_counter()-t; end=stamp(); print(f'[{name}] TIMEOUT {end} elapsed={elapsed:.3f}s budget={timeout}s',flush=True)
        return {'name':name,'start':start,'end':end,'elapsed_s':round(elapsed,3),'rc':124,'timeout':True,'failed_tests':[],'failed_js':[]}

def pytests(files, timeout=60, name='pytest'):
    return run_stage(name,[PY,'-m','pytest','-q',*map(str,files)],timeout=timeout)

def js_all(timeout=30):
    script='''const fs=require('fs'),cp=require('child_process'),p=require('path');let pass=0,failed=[];for(const f of fs.readdirSync('tests').filter(x=>x.endsWith('.js')).sort()){const r=cp.spawnSync(process.execPath,[p.join('tests',f)],{encoding:'utf8'});if(r.status===0)pass++;else failed.push(f);}for(const f of failed)console.log('FAILED_JS:'+f);console.log(JSON.stringify({pass,fail:failed.length,total:pass+failed.length}));process.exit(0);'''
    return run_stage('js-all',['node','-e',script],timeout=timeout)

FAST_PY=[
 TESTS/'test_r3_gate_state_contract_alignment_tdd.py',
 TESTS/'test_r3_required_path_survivability_tdd.py',
]

def fast():
    rows=[]
    rows.append(run_stage('runtime-fast',[PY,str(TESTS/'run_regression_suite.py')],timeout=30))
    rows.append(pytests([p for p in FAST_PY if p.exists()],timeout=45,name='python-targeted'))
    app=ROOT/'web/app.js'
    if app.exists(): rows.append(run_stage('js-syntax',['node','--check',str(app)],timeout=10))
    return rows

def affected(changed:list[str]):
    rows=fast(); names=' '.join(changed).lower()
    if any(x in names for x in ('web/','.js','.css','.html')): rows.append(js_all(30))
    elif any(x in names for x in ('compiler','ordo_yaml_semantics','generated_playbook_profile_adapter')):
        files=sorted(TESTS.glob('*compiler*.py'))+sorted(TESTS.glob('*language_conformance*.py'))+sorted(TESTS.glob('*profile*adapter*.py'))
        rows.append(pytests(files[:20],timeout=60,name='python-affected-compiler'))
    elif any(x in names for x in ('editor_service','alpha20_runtime','runtime')):
        pats=['*package_tool*.py','*deterministic*.py','*materialization*.py','*runtime*.py','*recovery*.py']
        files=[]
        for pat in pats: files.extend(TESTS.glob(pat))
        rows.append(pytests(sorted(set(files))[:24],timeout=60,name='python-affected-runtime'))
    return rows

def full():
    rows=[]
    files=[p for p in sorted(TESTS.glob('test_*.py')) if p.name!='test_r3_manifest_consistency.py']
    # Four process-isolated shards cut the exhaustive wall time roughly in half
    # while retaining isolation. This mode is still explicit/pre-release only.
    shards=[[] for _ in range(4)]
    for i,p in enumerate(files): shards[i%4].append(p)
    def one(i,shard): return pytests(shard,timeout=75,name=f'python-full-shard-{i+1}')
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs=[ex.submit(one,i,sh) for i,sh in enumerate(shards)]
        for f in as_completed(futs): rows.append(f.result())
    rows.append(js_all(45))
    return rows

def _baseline():
    p=TESTS/'KNOWN_BASELINE_FAILURES.json'
    return json.loads(p.read_text()) if p.exists() else {'python':[],'js':[]}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('mode',choices=['fast','affected','full']); ap.add_argument('--changed',action='append',default=[]); ap.add_argument('--report')
    a=ap.parse_args(); t=time.perf_counter(); started=stamp();
    rows=fast() if a.mode=='fast' else affected(a.changed) if a.mode=='affected' else full()
    baseline_match=None
    if a.mode=='full':
        b=_baseline(); got_py=sorted({x for r in rows for x in r.get('failed_tests',[])}); got_js=sorted({x for r in rows for x in r.get('failed_js',[])})
        baseline_match=(got_py==sorted(b.get('python',[])) and got_js==sorted(b.get('js',[])))
    report={'mode':a.mode,'start':started,'end':stamp(),'elapsed_s':round(time.perf_counter()-t,3),'stages':rows,'baseline_match':baseline_match}
    print('VERIFY_EDITOR '+json.dumps(report,ensure_ascii=False),flush=True)
    if a.report: Path(a.report).write_text(json.dumps(report,indent=2)+'\n')
    if any(r['timeout'] for r in rows): return 124
    if a.mode=='full': return 0 if baseline_match else 1
    return 0 if all(r['rc']==0 for r in rows) else 1
if __name__=='__main__': raise SystemExit(main())
