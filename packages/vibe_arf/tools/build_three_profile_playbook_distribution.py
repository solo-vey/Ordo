#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, tempfile, zipfile, shutil
from pathlib import Path
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parent))
from materialize_profile_dependency_closure import build_closure
from materialize_model_run_projection import project as materialize_model_projection
FIXED=(1980,1,1,0,0,0)
def h(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return h(Path(p).read_bytes())
def info(rel,executable=False):
    z=zipfile.ZipInfo(rel,FIXED); z.compress_type=zipfile.ZIP_DEFLATED; z.create_system=3; z.external_attr=((0o100755 if executable else 0o100644)<<16); return z
def put(z,rel,data): z.writestr(info(rel,rel=='cli_embedded/ordo'),data)
def identity(root,files):
    hh=hashlib.sha256(); rows=[]
    for rel in files:
        b=(root/rel).read_bytes(); rows.append({'path':rel,'sha256':h(b)}); hh.update(rel.encode()+b'\0'+b+b'\0')
    return hh.hexdigest(),rows
def version(root): return str((yaml.safe_load((root/'ordo.yml').read_text()) or {}).get('version',''))
def member_hash(rows):
    hh=hashlib.sha256()
    for rel,digest in sorted(rows): hh.update(rel.encode()+b'\0'+digest.encode()+b'\0')
    return hh.hexdigest()
def continuity(root,profile,sid,srows,member_rows,closure_name,closure_bytes,start_files,stem):
    return {'schema_version':'1.0','profile':profile,'version':version(root),'canonical_source_identity':sid,'source_identity_files':srows,
      'dependency_closure_sha256':h(closure_bytes) if closure_bytes is not None else None,'member_set_sha256':member_hash(member_rows),
      'startup_files':[{'path':x,'sha256':sha_file(root/x)} for x in start_files if (root/x).is_file()],
      'test_projection':({'mode':'retained_contract','path':'tests/test_cases.yaml','sha256':sha_file(root/'tests/test_cases.yaml')} if (root/'tests/test_cases.yaml').is_file() else None),
      'packaging_policy_sha256':sha_file(root/'source/packaging-continuity-policy.json'),'validator_applicability_policy_sha256':sha_file(root/'source/validator-applicability-policy.json'),
      'rebuild_recipe':{'builder':'tools/build_three_profile_playbook_distribution.py','profile':profile,'stem':stem,'source':'canonical source package only'},
      'closure_manifest':closure_name}
def build_from_rows(root,out,profile,rels,sid,srows,closure_name=None,closure_data=None,stem='VIBE_ARF_CURRENT'):
    payload=[]
    for rel in sorted(set(rels)):
        if rel in {'DISTRIBUTION_MANIFEST.json','PACKAGE_CONTINUITY_MANIFEST.json',closure_name}: continue
        p=root/rel
        if p.is_file(): payload.append((rel,p.read_bytes()))
    closure_bytes=(json.dumps(closure_data,ensure_ascii=False,indent=2)+'\n').encode() if closure_data is not None else None
    if closure_name and closure_bytes is not None: payload.append((closure_name,closure_bytes))
    member_rows=[(rel,h(data)) for rel,data in payload]
    cm=continuity(root,profile,sid,srows,member_rows,closure_name,closure_bytes,(json.loads((root/'DISTRIBUTION_PACKAGE_CONTRACT.json').read_text())['profiles'][profile].get('start_files',[])),stem)
    dm={'schema_version':'3.0','distribution':profile,'version':version(root),'source_identity_sha256':sid,'source_identity_files':srows,'continuity_manifest':'PACKAGE_CONTINUITY_MANIFEST.json'}
    payload += [('DISTRIBUTION_MANIFEST.json',(json.dumps(dm,ensure_ascii=False,indent=2)+'\n').encode()),('PACKAGE_CONTINUITY_MANIFEST.json',(json.dumps(cm,ensure_ascii=False,indent=2)+'\n').encode())]
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for rel,data in sorted(payload): put(z,rel,data)
def edit_members_from_prod(prodzip):
    with zipfile.ZipFile(prodzip) as z: return [(i.filename,z.read(i.filename)) for i in z.infolist() if i.filename not in {'DISTRIBUTION_MANIFEST.json','PACKAGE_CONTINUITY_MANIFEST.json'}]
def build_edit(root,out,sid,srows,stem):
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td)/'edit.zip'; subprocess.run([sys.executable,str(root/'tools/build_production_playbook_package.py'),str(root),str(tmp),'--profile','production'],check=True)
        payload=edit_members_from_prod(tmp); member_rows=[(rel,h(data)) for rel,data in payload]
        cm=continuity(root,'EDIT',sid,srows,member_rows,None,None,json.loads((root/'DISTRIBUTION_PACKAGE_CONTRACT.json').read_text())['profiles']['EDIT'].get('start_files',[]),stem)
        dm={'schema_version':'3.0','distribution':'EDIT','version':version(root),'source_identity_sha256':sid,'source_identity_files':srows,'continuity_manifest':'PACKAGE_CONTINUITY_MANIFEST.json'}
        payload += [('DISTRIBUTION_MANIFEST.json',(json.dumps(dm,ensure_ascii=False,indent=2)+'\n').encode()),('PACKAGE_CONTINUITY_MANIFEST.json',(json.dumps(cm,ensure_ascii=False,indent=2)+'\n').encode())]
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            for rel,data in sorted(payload): put(z,rel,data)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('output_dir'); ap.add_argument('--stem',default='VIBE_ARF_CURRENT'); ap.add_argument('--profiles',nargs='+',default=['EDIT','CLI_RUN','MODEL_RUN']); a=ap.parse_args()
    root=Path(a.root).resolve(); od=Path(a.output_dir).resolve(); od.mkdir(parents=True,exist_ok=True); c=json.loads((root/'DISTRIBUTION_PACKAGE_CONTRACT.json').read_text()); sid,srows=identity(root,c['source_identity_files']); result={'status':'PASS','source_identity_sha256':sid,'profiles':{}}
    for profile in [x.upper() for x in a.profiles]:
        out=od/f'{a.stem}_{profile}.zip'
        if profile=='EDIT': build_edit(root,out,sid,srows,a.stem)
        else:
            build_root=root
            projection_manifest=None
            td=None
            if profile=='MODEL_RUN':
                td=tempfile.TemporaryDirectory(); build_root=Path(td.name)/'model_run_projection'
                projection_manifest=materialize_model_projection(root,build_root)
            closure=build_closure(build_root,profile)
            if profile=='MODEL_RUN':
                bad=[x for x in closure.get('rejected_forbidden_references',[]) if x.get('reason','').startswith('explicit_ref:source/program.ordo.yaml')]
                if bad: raise SystemExit('MODEL_RUN_FORBIDDEN_RUNTIME_REFERENCE:'+','.join(sorted({x['path'] for x in bad})[:20]))
                # Carry projection lineage as a runtime-safe root artifact.
                rels=[x['path'] for x in closure['files']] + ['MODEL_RUN_SUPPORT_PROJECTION.json']
            else:
                rels=[x['path'] for x in closure['files']]
            build_from_rows(build_root,out,profile,rels,sid,srows,profile+'_PACKAGE_DEPENDENCY_CLOSURE.json',closure,a.stem)
            if td is not None: td.cleanup()
        result['profiles'][profile]=str(out)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
