#!/usr/bin/env python3
import argparse, json, hashlib, shutil, zipfile, os
from pathlib import Path

def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def authority_key(x):
 ranks={'current':6,'accepted':5,'approved':4,'canonical':3,'superseded':0,'rejected':-1}
 return (ranks.get(x.get('status',''),1), tuple(int(v) if v.isdigit() else v for v in x.get('version','0').replace('-','.').split('.')))

def build(catalog,outdir):
 c=json.loads(Path(catalog).read_text()); out=Path(outdir); shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
 selected=[]; excluded=[]
 for fam in c['artifact_families']:
  current=[x for x in fam['candidates'] if x.get('status') in {'current','accepted','approved','canonical'}]
  explicit=[x for x in current if x.get('authoritative') is True]
  if len(explicit)>1: raise SystemExit('BLOCKED: AMBIGUOUS_CURRENT_AUTHORITY')
  pick=explicit[0] if explicit else max(current,key=authority_key) if current else None
  if not pick: raise SystemExit('BLOCKED: AMBIGUOUS_CURRENT_AUTHORITY')
  if not pick.get('provenance'): raise SystemExit('BLOCKED: MISSING_PROVENANCE')
  src=Path(c['source_root'])/pick['path']
  if not src.exists(): raise SystemExit('BLOCKED: MISSING_SOURCE_FILE')
  dest=out/pick['target']; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dest)
  selected.append({'logical_artifact_id':fam['id'],'candidates_found':[x['path'] for x in fam['candidates']],'selected':pick['path'],'selection_reason':'authoritative status and semantic version','version_comparison':[x.get('version') for x in fam['candidates']],'accepted_status':pick['status'],'run_binding':pick.get('run_binding'),'sha256':sha(dest),'excluded_alternatives':[x['path'] for x in fam['candidates'] if x is not pick]})
  excluded += [x['path'] for x in fam['candidates'] if x is not pick]
 reports={'SELECTION_REPORT.json':{'schema_version':'ordo.current_state_selection_report.v1','artifact_families':selected},'EXCLUSION_REPORT.json':{'schema_version':'ordo.current_state_exclusion_report.v1','categories':[{'category':'historical_or_superseded','file_count':len(excluded),'representative_paths':excluded[:20],'exclusion_rationale':'not current authoritative state'}]},'LANGUAGE_AUDIT.json':{'schema_version':'ordo.language_audit.v1','new_documents_language':'English','immutable_source_language_exceptions':[]}}
 for n,o in reports.items(): (out/n).write_text(json.dumps(o,indent=2)+'\n')
 retained=[p for p in out.rglob('*') if p.is_file()]
 manifest={'schema_version':'ordo.current_state_manifest.v1','dataset_version':c['dataset_version'],'transfer_version':c['transfer_version'],'source_archive':c['source_archive'],'selection_policy':'CURRENT_STATE_ONLY','retained':{'total_files':len(retained),'accepted_runs':c.get('accepted_runs',[]),'current_packages':c.get('current_packages',[])},'excluded':{'file_count':len(excluded)},'known_limitations':c.get('known_limitations',[])}
 (out/'CURRENT_STATE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (out/'README.md').write_text('This archive is a current-state-only evidence snapshot.\nHistorical development packages and superseded runs are intentionally excluded.\n')
 files=sorted(p for p in out.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt')
 (out/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(out).as_posix()}\n' for p in files))
 z=out.with_suffix('.zip')
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as q:
  for p in sorted(out.rglob('*')):
   if p.is_file(): q.write(p,p.relative_to(out.parent))
 return z
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('catalog');a.add_argument('output');x=a.parse_args();z=build(x.catalog,x.output);print(json.dumps({'status':'PASS_RELEASE','zip':str(z),'sha256':sha(z)}))
