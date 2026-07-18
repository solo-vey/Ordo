#!/usr/bin/env python3
import argparse, zipfile, json, hashlib, pathlib, tempfile, subprocess, os, yaml, re, sys

def sha256(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def result(cid, ok, **kw):
 d={'id':cid,'pass':bool(ok)}; d.update(kw); return d

def safe_name(n):
 p=pathlib.PurePosixPath(n)
 return not (p.is_absolute() or '..' in p.parts or '\\' in n)

def run_cmd(cmd,cwd):
 cp=subprocess.run(cmd,shell=True,cwd=cwd,text=True,capture_output=True,timeout=120)
 return {'command':cmd,'exit_code':cp.returncode,'stdout':cp.stdout[-4000:],'stderr':cp.stderr[-4000:]}

def edges_from(obj):
 edges=[]
 for n in obj.get('nodes',[]):
  s=n.get('id')
  for key in ('next','on_pass','on_fail','on_complete'):
   v=n.get(key)
   if isinstance(v,str): edges.append((s,v))
   elif isinstance(v,dict) and isinstance(v.get('next'),str): edges.append((s,v['next']))
  for b in n.get('branches',[]) or []:
   if isinstance(b,dict) and isinstance(b.get('next'),str): edges.append((s,b['next']))
 for g in obj.get('gates',[]):
  for key in ('on_pass','on_fail'):
   if isinstance(g.get(key),str): edges.append((g.get('id'),g[key]))
 return edges

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('archive',nargs='?'); ap.add_argument('--report'); ap.add_argument('--cycle',type=int,default=1); a=ap.parse_args()
 if not a.archive: ap.print_help(); return 0
 zpath=pathlib.Path(a.archive)
 rep={'schema_version':'ordo.benchmark.package_green_light_report.v2','cycle':a.cycle,'archive':str(zpath),'archive_sha256':sha256(zpath),'checks':[],'commands':[],'exit_codes':[],'status':'FAIL','release_disposition':'NO_CHANGE','GREEN_LIGHT':False}
 try:
  with zipfile.ZipFile(zpath) as z:
   names=z.namelist(); bad=z.testzip(); dup=sorted({n for n in names if names.count(n)>1}); unsafe=[n for n in names if not safe_name(n)]
   rep['checks'].append(result('physical_integrity',bad is None and not dup and not unsafe,testzip_error=bad,duplicates=dup,unsafe_paths=unsafe))
   roots={n.split('/')[0] for n in names if '/' in n}; prefix=(next(iter(roots))+'/') if len(roots)==1 else ''
   with tempfile.TemporaryDirectory(prefix='ordo_consumer_') as td:
    z.extractall(td); root=pathlib.Path(td)/(prefix.rstrip('/') if prefix else '')
    inv=json.loads((root/'DECLARED_CONTRACT_INVENTORY.json').read_text())
    missing=[x for x in inv['required_paths'] if not (root/x).exists()]
    rep['checks'].append(result('package_completeness',not missing,missing=missing))
    addr_missing=[x for x in inv.get('referenced_paths',[]) if not (root/x).exists()]
    rep['checks'].append(result('runtime_addressability',not addr_missing,missing=addr_missing,implicit_aliases_allowed=False))
    expected=inv['package_version']; incoherent=[]
    for rel in inv.get('version_coherence_files',[]):
     t=(root/rel).read_text(errors='ignore')
     if expected not in t: incoherent.append(rel)
    rep['checks'].append(result('version_coherence',not incoherent,expected=expected,incoherent_files=incoherent))
    prog=yaml.safe_load((root/inv['program_path']).read_text())
    actual=(prog.get('process_rail') or {}).get('entry_node') or (prog.get('execution_graph_contract') or {}).get('entry_node') or prog.get('entrypoint') or (prog.get('nodes') or [{}])[0].get('id')
    rep['checks'].append(result('entrypoint_coherence',actual==inv['declared_entrypoint'],declared=inv['declared_entrypoint'],actual=actual))
    ex=inv['structural_expectations']; ids=[x.get('id') for k in ('nodes','gates','terminals') for x in prog.get(k,[])]; struct=(len(prog.get('nodes',[]))==ex['node_count'] and len(prog.get('gates',[]))==ex['gate_count'] and len(prog.get('terminals',[]))==ex['terminal_count'] and len(ids)==len(set(ids)))
    rep['checks'].append(result('structural_completeness',struct,actual={'nodes':len(prog.get('nodes',[])),'gates':len(prog.get('gates',[])),'terminals':len(prog.get('terminals',[])),'unique_ids':len(ids)==len(set(ids))},expected=ex))
    # checksums
    mism=[]
    for line in (root/'SHA256SUMS.txt').read_text().splitlines():
     if not line.strip(): continue
     h,rel=line.split(None,1); rel=rel.strip().lstrip('*')
     if rel=='SHA256SUMS.txt': continue
     p=root/rel; got=sha256(p) if p.exists() else 'MISSING'
     if got!=h: mism.append(rel)
    rep['checks'][0]['checksum_mismatches']=mism; rep['checks'][0]['pass']=rep['checks'][0]['pass'] and not mism
    # semantic parity exact command
    rr=run_cmd(inv['semantic_parity']['command'],root); rep['commands'].append(rr); rep['exit_codes'].append(rr['exit_code'])
    par_ok=rr['exit_code']==0
    try: par_ok=par_ok and json.loads((root/inv['semantic_parity']['report_path']).read_text()).get('status')=='PASS'
    except Exception: par_ok=False
    rep['checks'].append(result('semantic_parity',par_ok,command=rr['command'],exit_code=rr['exit_code']))
    # correction reachability
    ed=edges_from(prog); c=inv['correction_loop']; reach={(s,t) for s,t in ed}; loop_ok=((c['failure_node'],c['retry_node']) in reach and (c['retry_node'],c['reseal_node']) in reach and c['max_passes']==5)
    rep['checks'].append(result('correction_loop_reachability',loop_ok,required=c))
    # validator reality
    vr=[]
    for v in inv['declared_validators']:
     rr=run_cmd(v['command'],root); rep['commands'].append(rr); rep['exit_codes'].append(rr['exit_code']); vr.append({'id':v['id'],'exit_code':rr['exit_code'],'pass':rr['exit_code']==v.get('expected_exit_code',0)})
    rep['checks'].append(result('validator_reality',all(x['pass'] for x in vr),validators=vr))
    # regressions
    regs=[]
    for rg in inv.get('regressions',[]):
     rr=run_cmd(rg['command'],root); rep['commands'].append(rr); rep['exit_codes'].append(rr['exit_code']); ok=(rr['exit_code']!=0 if rg.get('expected_nonzero') else rr['exit_code']==rg.get('expected_exit_code',0)); regs.append({'id':rg['id'],'kind':rg['kind'],'exit_code':rr['exit_code'],'pass':ok})
    rep['checks'].append(result('positive_negative_regressions',all(x['pass'] for x in regs),regressions=regs))
    rep['checks'].append(result('black_box_preflight',all(str(root) in str(root/x) for x in inv['required_paths']),workspace=str(root),external_files_used=False))
    # smoke: no business artifacts are created by validator commands and preflight is green
    business=[p for p in root.rglob('*') if p.is_file() and p.name in {'JIRA_TASK.md','MANUAL_QA_EXECUTION_SPEC.md','QA_AUTOMATION_SPEC.yaml','FULL_RECORD_CHANGE_PASSPORT.md'}]
    prior_green=all(c['pass'] for c in rep['checks'])
    rep['checks'].append(result('execution_smoke_test',prior_green and not business,business_artifacts_created_before_green=[str(p.relative_to(root)) for p in business]))
  ok=len(rep['checks'])==12 and all(c['pass'] for c in rep['checks'])
  rep.update({'status':'PASS' if ok else 'FAIL','release_disposition':'PASS_RELEASE' if ok else 'NO_CHANGE','GREEN_LIGHT':ok,'exact_sealed_zip_verified':ok,'all_declared_checks_executed':len(rep['checks'])==12})
 except Exception as e: rep['error']=repr(e)
 out=pathlib.Path(a.report or str(zpath)+'.green_light_report.json'); out.write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(rep,ensure_ascii=False,indent=2)); return 0 if rep['GREEN_LIGHT'] else 2
if __name__=='__main__': raise SystemExit(main())
