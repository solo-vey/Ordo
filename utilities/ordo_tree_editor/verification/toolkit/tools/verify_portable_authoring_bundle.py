#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile,sys,os,time,yaml,importlib.util
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd,**kw): return subprocess.run(cmd,capture_output=True,text=True,**kw)
def main():
 t=time.monotonic();checks=[]
 pm=json.loads((R/'PORTABLE_PACKAGE_MANIFEST.json').read_text());pbad=[]
 for x in pm.get('immutable_files',[]):
  p=R/x['path']; exp=x['sha256']
  if not p.is_file() or sha(p)!=exp:pbad.append(x['path'])
 checks.append({'id':'PACKAGE_MANIFEST','status':'PASS' if not pbad else 'FAIL','bad':pbad[:100]})
 m=json.loads((R/'canonical_support/CANONICAL_SUPPORT_MANIFEST.json').read_text());bad=[]
 for x in m['files']:
  p=R/x['path'];exp=x.get('effective_sha256') or x['source_sha256']
  if not p.is_file() or sha(p)!=exp:bad.append(x['path'])
 checks.append({'id':'SUPPORT_HASHES','status':'PASS' if not bad else 'FAIL','bad':bad})
 # root/embedded language mirror must be exact
 mirror=[]
 for p in (R/'language').rglob('*'):
  if p.is_file():
   q=R/'cli_embedded'/'language'/p.relative_to(R/'language')
   if not q.is_file() or sha(p)!=sha(q): mirror.append(str(p.relative_to(R)))
 checks.append({'id':'LANGUAGE_MIRROR','status':'PASS' if not mirror else 'FAIL','bad':mirror[:50]})
 p=run([str(R/'cli_embedded/ordo'),'runtime-status',str(R)]);checks.append({'id':'SELF_RUNTIME','status':'PASS' if p.returncode==0 else 'FAIL','tail':p.stdout[-500:]+p.stderr[-500:]})
 with tempfile.TemporaryDirectory() as td:
  pkg=Path(td)/'smoke';env=os.environ.copy();env['PYTHONPATH']=str(R/'cli_embedded/ordo_pkg')
  a=run([sys.executable,'-m','ordo.cli','init',str(pkg)],env=env);b=run([sys.executable,'-m','ordo.cli','lint',str(pkg)],env=env) if a.returncode==0 else None;c=run([sys.executable,'-m','ordo.cli','compile',str(pkg)],env=env) if a.returncode==0 else None
  ok=a.returncode==0 and b and b.returncode==0 and c and c.returncode==0;checks.append({'id':'ISOLATED_AUTHORING_SMOKE','status':'PASS' if ok else 'FAIL','init':a.returncode,'lint':None if b is None else b.returncode,'compile':None if c is None else c.returncode})
 # editor validator in portable root layout
 ep=R/'utilities/ordo_tree_editor/editor_service.py'; editor_ok=False; editor_issues=[]
 try:
  spec=importlib.util.spec_from_file_location('portable_editor_service',ep);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  source=yaml.safe_load((R/'source/program.ordo.yaml').read_text(encoding='utf-8'));er=mod.validate_source(source);editor_ok=er.get('status')=='passed';editor_issues=er.get('issues',[])
 except Exception as exc: editor_issues=[{'exception':repr(exc)}]
 checks.append({'id':'EDITOR_VALIDATION','status':'PASS' if editor_ok else 'FAIL','issues':editor_issues[:20]})
 # visual graph generator smoke
 with tempfile.TemporaryDirectory() as td:
  out=Path(td)/'graph.mmd';g=run([sys.executable,str(R/'utilities/ordo_visual_graph_generator/ordo_graph.py'),str(R/'source/program.ordo.yaml'),'--format','mmd','--out',str(out)])
  checks.append({'id':'GRAPH_RENDER_SMOKE','status':'PASS' if g.returncode==0 and out.is_file() else 'FAIL','tail':g.stdout[-500:]+g.stderr[-500:]})
 st='PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL';o={'schema_version':'1.1','status':st,'checks':checks,'duration_seconds':round(time.monotonic()-t,3)};(R/'reports/ALPHA9_PORTABLE_VERIFY.json').write_text(json.dumps(o,indent=2)+"\n",encoding='utf-8');print(json.dumps(o,indent=2));return 0 if st=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
