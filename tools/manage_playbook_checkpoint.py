#!/usr/bin/env python3
import argparse,hashlib,json,shutil,tempfile,zipfile
from pathlib import Path

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tree_hash(root):
 h=hashlib.sha256()
 for p in sorted(Path(root).rglob('*')):
  if p.is_file(): h.update(p.relative_to(root).as_posix().encode()+b'\0'+hashlib.sha256(p.read_bytes()).digest())
 return h.hexdigest()
def create(package,out,state=None):
 package=Path(package).resolve(); out=Path(out).resolve(); rel=json.loads((package/'playbook_release.json').read_text())
 checkpoint_id=f"{rel['playbook_id']}@{rel['playbook_version']}"
 with tempfile.TemporaryDirectory() as td:
  stage=Path(td)/'checkpoint'; shutil.copytree(package,stage/'package')
  if state: shutil.copy2(state,stage/'runtime_state.json')
  manifest={'schema_version':'ordo.playbook.rollback_checkpoint.v1','checkpoint_id':checkpoint_id,'playbook_id':rel['playbook_id'],'playbook_version':rel['playbook_version'],'package_sha256':tree_hash(package),'archive':{'filename':out.name},'runtime_state':{'included':bool(state)},'verification':{'created':True,'restore_round_trip':False}}
  (stage/'CHECKPOINT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
  lines=[]
  for p in sorted(stage.rglob('*')):
   if p.is_file() and p.name!='SHA256SUMS.txt': lines.append(f"{sha(p)}  {p.relative_to(stage).as_posix()}")
  (stage/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')
  with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
   for p in sorted(stage.rglob('*')):
    if p.is_file(): z.write(p,Path('checkpoint')/p.relative_to(stage))
 return verify(out,update=False)
def verify(archive,update=False):
 archive=Path(archive)
 with tempfile.TemporaryDirectory() as td:
  td=Path(td)
  with zipfile.ZipFile(archive) as z:
   if z.testzip(): raise SystemExit('zip_integrity_failed')
   z.extractall(td)
  root=td/'checkpoint'; failures=[]
  for line in (root/'SHA256SUMS.txt').read_text().splitlines():
   exp,rel=line.split('  ',1); p=root/rel
   if not p.is_file() or sha(p)!=exp: failures.append(rel)
  m=json.loads((root/'CHECKPOINT_MANIFEST.json').read_text()); r=json.loads((root/'package/playbook_release.json').read_text())
  identity=(m['playbook_id']==r['playbook_id'] and m['playbook_version']==r['playbook_version'])
  result={'archive':archive.name,'archive_sha256':sha(archive),'zip_integrity':'passed','checksums':'passed' if not failures else 'failed','failures':failures,'identity':'passed' if identity else 'failed','restore_round_trip':'passed' if not failures and identity else 'failed','checkpoint_id':m['checkpoint_id']}
  if failures or not identity: raise SystemExit(json.dumps(result))
  return result
if __name__=='__main__':
 ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
 c=sp.add_parser('create'); c.add_argument('package'); c.add_argument('out'); c.add_argument('--state')
 v=sp.add_parser('verify'); v.add_argument('archive')
 a=ap.parse_args(); result=create(a.package,a.out,a.state) if a.cmd=='create' else verify(a.archive)
 print(json.dumps(result,indent=2))
