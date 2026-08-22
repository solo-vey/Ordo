#!/usr/bin/env python3
from pathlib import Path
import json, tempfile, shutil, subprocess, zipfile, hashlib, sys
R=Path(__file__).resolve().parents[1]
checks=[]
def ck(n,c,d=''): checks.append((n,bool(c),d))

contract=json.loads((R/'PRODUCTION_PACKAGE_CONTRACT.json').read_text())
gen=next((x for x in contract.get('artifact_classes',[]) if x.get('class')=='generated_outputs'),{})
ck('generated_outputs_not_broad_optional', gen.get('default_inclusion')!='optional')
ck('safe_manifest_declared', 'safe_delivery_manifest' in contract)
ck('safe_manifest_path', contract.get('safe_delivery_manifest')=='generated_outputs/PRODUCTION_DELIVERABLES.json')

builder=(R/'tools/build_production_playbook_package.py').read_text()
validator=(R/'tools/validate_production_playbook_package.py').read_text()
ck('builder_enforces_manifest', 'PRODUCTION_DELIVERABLES.json' in builder and 'production_deliverable' in builder)
ck('builder_hash_checks', 'sha256' in builder and 'GENERATED_OUTPUT_HASH_MISMATCH' in builder)
ck('validator_enforces_manifest', 'PRODUCTION_DELIVERABLES.json' in validator and 'UNDECLARED_GENERATED_OUTPUT' in validator)
ck('forbid_unsafe_roles', 'simulation' in builder and 'evaluator' in builder and 'reference' in builder)
ck('placeholder_ignored', ".gitkeep" in builder and ".keep" in builder)

# behavior fixture from real package root clone-light: copy required root artifacts + contract + source policy + generated outputs
with tempfile.TemporaryDirectory() as td:
    root=Path(td)/'pkg'; root.mkdir()
    # minimal root files required by builder contract
    for rel in contract.get('required_root_artifacts',[]):
        src=R/rel; dst=root/rel; dst.parent.mkdir(parents=True,exist_ok=True)
        if src.is_file(): shutil.copy2(src,dst)
        else: dst.write_text('x')
    shutil.copy2(R/'PRODUCTION_PACKAGE_CONTRACT.json',root/'PRODUCTION_PACKAGE_CONTRACT.json')
    sp=R/'source/generated-playbook-production-package-policy.json'
    if sp.exists():
        (root/'source').mkdir(exist_ok=True); shutil.copy2(sp,root/'source/generated-playbook-production-package-policy.json')
    go=root/'generated_outputs'; go.mkdir()
    (go/'.gitkeep').write_text('')
    (go/'undeclared.md').write_text('secret simulated best')
    out=Path(td)/'out.zip'
    p=subprocess.run([sys.executable,str(R/'tools/build_production_playbook_package.py'),str(root),str(out)],capture_output=True,text=True)
    ck('undeclared_output_rejected', p.returncode!=0 and 'UNDECLARED_GENERATED_OUTPUT' in (p.stdout+p.stderr), p.stdout+p.stderr)

    (go/'undeclared.md').unlink()
    data=b'final delivery'
    (go/'deliverable.md').write_bytes(data)
    manifest={'schema_version':'1.0','deliverables':[{'path':'generated_outputs/deliverable.md','production_deliverable':True,'role':'declared_delivery','sha256':hashlib.sha256(data).hexdigest()}]}
    (go/'PRODUCTION_DELIVERABLES.json').write_text(json.dumps(manifest))
    p=subprocess.run([sys.executable,str(R/'tools/build_production_playbook_package.py'),str(root),str(out)],capture_output=True,text=True)
    ck('declared_safe_output_included', p.returncode==0, p.stdout+p.stderr)
    if out.exists():
        with zipfile.ZipFile(out) as z:
            names=set(z.namelist())
        ck('deliverable_present','generated_outputs/deliverable.md' in names)
        ck('delivery_manifest_present','generated_outputs/PRODUCTION_DELIVERABLES.json' in names)

    # unsafe role must fail despite production_deliverable flag
    manifest['deliverables'][0]['role']='simulation'
    (go/'PRODUCTION_DELIVERABLES.json').write_text(json.dumps(manifest))
    p=subprocess.run([sys.executable,str(R/'tools/build_production_playbook_package.py'),str(root),str(out)],capture_output=True,text=True)
    ck('unsafe_role_rejected', p.returncode!=0 and 'UNSAFE_GENERATED_OUTPUT_ROLE' in (p.stdout+p.stderr), p.stdout+p.stderr)

failed=[n for n,c,d in checks if not c]
print(json.dumps({'status':'PASS' if not failed else 'FAIL','passed':sum(c for _,c,_ in checks),'total':len(checks),'failed':failed},indent=2))
sys.exit(0 if not failed else 1)
