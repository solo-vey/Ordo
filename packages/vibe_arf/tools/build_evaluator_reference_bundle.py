#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, hashlib, shutil
from pathlib import Path

def h(p: Path): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package_root'); ap.add_argument('selection_json'); ap.add_argument('--output-dir',default='evaluator/reference_bundle')
    a=ap.parse_args(); root=Path(a.package_root).resolve(); selection=json.loads(Path(a.selection_json).read_text())
    catp=root/'analyst_context/context_catalog.json'; catalog=json.loads(catp.read_text()) if catp.is_file() else {'records':[]}
    byid={r.get('source_id'):r for r in catalog.get('records',[])}
    refs=selection.get('selected_references',selection.get('references',selection.get('reference_selection',[])))
    out=root/a.output_dir
    if out.exists(): shutil.rmtree(out)
    files=out/'files'; files.mkdir(parents=True,exist_ok=True)
    manifest={'schema_version':'1.0','bundle_id':'EVALUATOR_REFERENCE_INPUT_BUNDLE','access_scope':'evaluator_only','allowed_consumers':['comparative_evaluator'],'denied_consumers':['generator','optimizer'],'references':[]}
    for i,r in enumerate(refs):
        rid=r.get('source_id') or r.get('reference_id') or r.get('id')
        rec=byid.get(rid,{})
        if rec.get('refresh_required'):
            print(json.dumps({'status':'FAIL','code':'REFERENCE_REFRESH_REQUIRED','reference_id':rid})); return 2
        src=rec.get('stored_path') or r.get('stored_path') or r.get('path')
        if not src:
            print(json.dumps({'status':'FAIL','code':'REFERENCE_CONTENT_PATH_MISSING','reference_id':rid})); return 3
        sp=(root/src).resolve()
        if root not in sp.parents and sp!=root:
            print(json.dumps({'status':'FAIL','code':'REFERENCE_PATH_OUTSIDE_PACKAGE','reference_id':rid})); return 4
        if not sp.is_file():
            print(json.dumps({'status':'FAIL','code':'REFERENCE_FILE_MISSING','reference_id':rid,'path':src})); return 5
        dst=files/f'{i:03d}_{sp.name}'; shutil.copy2(sp,dst)
        manifest['references'].append({'reference_id':rid,'bundle_path':dst.relative_to(root).as_posix(),'sha256':h(dst),'weight':r.get('weight',r.get('relevance_weight')),'access_scope':'evaluator_only'})
    mp=out/'manifest.json'; mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'PASS','bundle_manifest':mp.relative_to(root).as_posix(),'reference_count':len(manifest['references'])},ensure_ascii=False)); return 0
if __name__=='__main__': raise SystemExit(main())
