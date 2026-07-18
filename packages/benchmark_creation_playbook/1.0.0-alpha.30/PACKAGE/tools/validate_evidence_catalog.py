#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def fail(code, detail, errors): errors.append({'code':code,'detail':detail})

def validate(package_root: Path) -> dict:
    errors=[]
    contract_path=package_root/'EVIDENCE_CATALOG_CONTRACT.json'
    cat_root=package_root/'EVIDENCE_BASE_CATALOG'
    if not contract_path.is_file(): return {'status':'FAIL','errors':[{'code':'MISSING_CONTRACT','detail':str(contract_path)}]}
    contract=json.loads(contract_path.read_text())
    for rel in contract['required_catalog_roots']:
        if not (cat_root/rel).is_dir(): fail('MISSING_CATALOG_ROOT',rel,errors)
    manifest_path=cat_root/'00_catalog'/'catalog_manifest.json'
    if not manifest_path.is_file(): fail('MISSING_MANIFEST',str(manifest_path),errors); manifest={'objects':[],'score_entries':[]}
    else: manifest=json.loads(manifest_path.read_text())
    ids=set(); objects={}
    valid_classes={x['id'] for x in contract['evidence_classes']}
    for obj in manifest.get('objects',[]):
        oid=obj.get('object_id')
        if not oid or oid in ids: fail('DUPLICATE_OR_MISSING_OBJECT_ID',str(oid),errors); continue
        ids.add(oid); objects[oid]=obj
        if obj.get('evidence_class') not in valid_classes: fail('UNKNOWN_EVIDENCE_CLASS',oid,errors)
        path=cat_root/obj.get('path','')
        if not path.is_file(): fail('OBJECT_PATH_MISSING',f'{oid}:{path}',errors)
        elif sha256(path)!=obj.get('sha256'): fail('OBJECT_SHA_MISMATCH',oid,errors)
        if obj.get('evidence_class')=='EXTERNAL_BLIND_RUN' and obj.get('blindness')!='EXTERNAL_BLIND': fail('BLIND_CLASS_CONTAMINATION',oid,errors)
    forbidden=set(contract['score_eligibility']['forbidden_statuses'])
    for score in manifest.get('score_entries',[]):
        run=objects.get(score.get('run_object_id'))
        if not run: fail('SCORE_RUN_NOT_FOUND',score.get('score_id'),errors); continue
        if run.get('evidence_class')!='EXTERNAL_BLIND_RUN': fail('INTERNAL_EVIDENCE_IN_SCORE_LEDGER',score.get('score_id'),errors)
        if run.get('lifecycle_state')!='CONFIRMED' or score.get('status') in forbidden: fail('INELIGIBLE_SCORE_STATE',score.get('score_id'),errors)
        bindings=run.get('bindings',{})
        for key in contract['binding_requirements']:
            if not bindings.get(key): fail('INCOMPLETE_RUN_BINDING',f"{score.get('score_id')}:{key}",errors)
    return {'schema_version':'ordo.evidence.catalog.validation.v1','status':'PASS' if not errors else 'FAIL','catalog_version':contract['catalog_version'],'object_count':len(objects),'score_count':len(manifest.get('score_entries',[])),'errors':errors}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package_root',nargs='?',default='.') ; ap.add_argument('--report')
    a=ap.parse_args(); report=validate(Path(a.package_root).resolve())
    out=json.dumps(report,indent=2,ensure_ascii=False)
    if a.report: Path(a.report).write_text(out+'\n')
    print(out); return 0 if report['status']=='PASS' else 2
if __name__=='__main__': raise SystemExit(main())
