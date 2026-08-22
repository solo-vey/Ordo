#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, io, json, subprocess, tempfile, zipfile
from pathlib import Path

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def identity(root, files):
    h=hashlib.sha256()
    rows=[]
    for rel in files:
        b=(root/rel).read_bytes(); rows.append({'path':rel,'sha256':sha_bytes(b)})
        h.update(rel.encode()+b'\0'+b+b'\0')
    return h.hexdigest(),rows

def add_manifest_copy(src_zip:Path,out_zip:Path,dist:str,source_id:str,source_rows:list):
    with zipfile.ZipFile(src_zip) as zin, zipfile.ZipFile(out_zip,'w',zipfile.ZIP_DEFLATED,allowZip64=True) as zout:
        for info in zin.infolist(): zout.writestr(info,zin.read(info.filename))
        m={'schema_version':'1.0','distribution':dist,'source_identity_sha256':source_id,'source_identity_files':source_rows}
        zout.writestr('DISTRIBUTION_MANIFEST.json',json.dumps(m,ensure_ascii=False,indent=2)+'\n')

def build_run(root:Path,out:Path,contract:dict,source_id:str,source_rows:list):
    closure=json.loads((root/'RUN_PACKAGE_DEPENDENCY_CLOSURE.json').read_text())
    run=contract['distributions']['RUN']; overrides=run.get('clean_seed_overrides',{})
    files=[]
    if out.exists():out.unlink()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,allowZip64=True) as z:
        for row in closure.get('files',[]):
            rel=row['path']; mat=row.get('materialization','copy')
            if mat=='clean_seed':
                b=(json.dumps(overrides[rel],ensure_ascii=False,indent=2)+'\n').encode()
            else:
                p=root/rel
                if not p.is_file(): raise SystemExit(f'RUN_CLOSURE_MISSING:{rel}')
                b=p.read_bytes()
                if row.get('sha256') and sha_bytes(b)!=row['sha256']: raise SystemExit(f'RUN_CLOSURE_HASH_MISMATCH:{rel}')
            z.writestr(rel,b); files.append({'path':rel,'bytes':len(b),'sha256':sha_bytes(b),'materialization':mat})
        # Closure itself is a runtime distribution proof, not a reachability dependency.
        b=(root/'RUN_PACKAGE_DEPENDENCY_CLOSURE.json').read_bytes(); z.writestr('RUN_PACKAGE_DEPENDENCY_CLOSURE.json',b)
        files.append({'path':'RUN_PACKAGE_DEPENDENCY_CLOSURE.json','bytes':len(b),'sha256':sha_bytes(b),'materialization':'distribution_proof'})
        m={'schema_version':'1.0','distribution':'RUN','source_identity_sha256':source_id,'source_identity_files':source_rows,'file_count':len(files),'files':files}
        z.writestr('DISTRIBUTION_MANIFEST.json',json.dumps(m,ensure_ascii=False,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('output_dir'); ap.add_argument('--stem',default='VIBE_ARF_CURRENT')
    a=ap.parse_args(); root=Path(a.root).resolve(); od=Path(a.output_dir).resolve(); od.mkdir(parents=True,exist_ok=True)
    c=json.loads((root/'DISTRIBUTION_PACKAGE_CONTRACT.json').read_text())
    # compiled/* is a derived runtime surface and may contain non-semantic build metadata; materialize it once per pair build.
    subprocess.run(['python',str(root/'tools/ordo_authoring.py'),'compile',str(root)],check=True,capture_output=True,text=True)
    sid,srows=identity(root,c['source_identity_files'])
    dev=od/f'{a.stem}_DEV.zip'; run=od/f'{a.stem}_RUN.zip'
    with tempfile.TemporaryDirectory() as td:
        tmp=Path(td)/'dev.zip'
        subprocess.run(['python',str(root/'tools/build_production_playbook_package.py'),str(root),str(tmp),'--profile','production'],check=True,capture_output=True,text=True)
        add_manifest_copy(tmp,dev,'DEV',sid,srows)
    build_run(root,run,c,sid,srows)
    print(json.dumps({'status':'PASS','source_identity_sha256':sid,'DEV':str(dev),'RUN':str(run),'dev_bytes':dev.stat().st_size,'run_bytes':run.stat().st_size},indent=2))
if __name__=='__main__': main()
