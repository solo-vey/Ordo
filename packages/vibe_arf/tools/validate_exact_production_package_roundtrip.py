#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, tempfile, zipfile
from pathlib import Path

def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('zip_path'); a=ap.parse_args()
    zp=Path(a.zip_path).resolve(); errors=[]
    if not zp.is_file():
        print(json.dumps({'status':'FAIL','code':'ZIP_MISSING','path':str(zp)},indent=2)); return 1
    with zipfile.ZipFile(zp) as z:
        names=z.namelist()
        for n in names:
            pp=Path(n)
            if pp.is_absolute() or '..' in pp.parts:
                errors.append({'code':'UNSAFE_ARCHIVE_PATH','path':n})
        if 'PRODUCTION_PACKAGE_MANIFEST.json' not in names:
            errors.append({'code':'MANIFEST_MISSING'})
            manifest={'files':[]}
        else:
            manifest=json.loads(z.read('PRODUCTION_PACKAGE_MANIFEST.json'))
        with tempfile.TemporaryDirectory(prefix='ordo_prod_exact_') as td:
            root=Path(td)
            if not errors:
                z.extractall(root)
            rows={r.get('path'):r for r in manifest.get('files',[]) if isinstance(r,dict) and r.get('path')}
            for rel,row in rows.items():
                p=root/rel
                if not p.is_file():
                    errors.append({'code':'EXTRACTED_FILE_MISSING','path':rel}); continue
                b=p.read_bytes(); actual=sha(b)
                if actual != row.get('sha256'):
                    errors.append({'code':'EXTRACTED_HASH_MISMATCH','path':rel,'expected':row.get('sha256'),'actual':actual})
                if len(b) != row.get('bytes'):
                    errors.append({'code':'EXTRACTED_SIZE_MISMATCH','path':rel,'expected':row.get('bytes'),'actual':len(b)})
            required=['source/program.ordo.yaml','PRODUCTION_PACKAGE_CONTRACT.json','PLAYBOOK_LAWS.md','authoring/information_object_catalog.yaml','authoring/ordo_projection.yaml']
            for rel in required:
                if not (root/rel).is_file(): errors.append({'code':'ROUNDTRIP_REQUIRED_FILE_MISSING','path':rel})
    out={'status':'PASS' if not errors else 'FAIL','producer':'tools/validate_exact_production_package_roundtrip.py','zip':str(zp),'zip_sha256':sha(zp.read_bytes()),'errors':errors,'validated_manifest_files':len(manifest.get('files',[]))}
    print(json.dumps(out,ensure_ascii=False,indent=2))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
