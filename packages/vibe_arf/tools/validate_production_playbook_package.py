#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,zipfile,hashlib

def fail(code, **extra):
    print(json.dumps({'status':'FAIL','code':code,**extra},indent=2)); return 1

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('zip_path'); a=ap.parse_args()
    with zipfile.ZipFile(a.zip_path) as z:
        bad=z.testzip(); names=set(z.namelist())
        if 'PRODUCTION_PACKAGE_MANIFEST.json' not in names:
            return fail('MANIFEST_MISSING')
        m=json.loads(z.read('PRODUCTION_PACKAGE_MANIFEST.json'))
        contract=json.loads(z.read('PRODUCTION_PACKAGE_CONTRACT.json')) if 'PRODUCTION_PACKAGE_CONTRACT.json' in names else {}
        generated=[n for n in names if n.startswith('generated_outputs/') and n!='generated_outputs/PRODUCTION_DELIVERABLES.json']
        delivery_manifest_rel=contract.get('safe_delivery_manifest','generated_outputs/PRODUCTION_DELIVERABLES.json')
        declared={}
        if generated:
            if delivery_manifest_rel not in names:
                return fail('GENERATED_OUTPUT_DELIVERY_MANIFEST_MISSING', generated=generated[:20])
            dm=json.loads(z.read(delivery_manifest_rel))
            declared={r.get('path'):r for r in dm.get('deliverables',[]) if r.get('path')}
            allowed=set(contract.get('generated_output_policy',{}).get('allowed_roles',['declared_delivery']))
            forbidden=set(contract.get('generated_output_policy',{}).get('forbidden_roles',['simulation','evaluator','reference','calibration','best_candidate','expected_output']))
            for n in generated:
                row=declared.get(n)
                if not row or row.get('production_deliverable') is not True:
                    return fail('UNDECLARED_GENERATED_OUTPUT', path=n)
                role=str(row.get('role',''))
                if role in forbidden or role not in allowed:
                    return fail('UNSAFE_GENERATED_OUTPUT_ROLE', path=n, role=role)
                actual=hashlib.sha256(z.read(n)).hexdigest(); expected=row.get('sha256')
                if not expected or actual!=expected:
                    return fail('GENERATED_OUTPUT_HASH_MISMATCH', path=n, expected=expected, actual=actual)
    required={'ordo.yml','source/program.ordo.yaml','authoring/information_object_catalog.yaml','authoring/information_flow_graph.yaml','authoring/ordo_projection.yaml','analyst_context/context_catalog.json','PLAYBOOK_LAWS.md'}
    missing=sorted(required-names)
    forbidden_files=sorted(n for n in names if '__pycache__/' in n or n.endswith(('.pyc','.pyo')))
    debug_prefixes=('change_records/','development_history/','reports/','runtime/','debug_handoff/')
    debug_allow_exact={'reports/CLI_VALIDATION_SUMMARY.md'}
    debug=[n for n in names if n not in debug_allow_exact and n.startswith(debug_prefixes)] if m.get('profile')=='production' else []
    classes={x.get('class') for x in m.get('files',[])}
    needed={'runtime','source','data_layer','analyst_context','authoring_templates','editor','validation','materialization'}
    missing_classes=sorted(needed-classes)
    status='PASS' if bad is None and not missing and not forbidden_files and not debug and not missing_classes else 'FAIL'
    print(json.dumps({'status':status,'profile':m.get('profile'),'files':len(names),'missing_required':missing,'missing_classes':missing_classes,'forbidden':forbidden_files[:20],'debug_leak':debug[:20],'generated_outputs':generated[:20],'integrity_bad_member':bad},indent=2))
    return 0 if status=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
