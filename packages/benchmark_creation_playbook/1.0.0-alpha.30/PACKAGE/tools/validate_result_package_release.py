#!/usr/bin/env python3
"""Fail-closed package-level self-validation gate for benchmark result packages."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path
from typing import Any
try:
    import yaml
except Exception as exc:
    raise SystemExit(f"PyYAML required: {exc}")

PASS='PASS'; FAIL='FAIL'

def load(path: Path) -> Any:
    text=path.read_text(encoding='utf-8')
    return yaml.safe_load(text) if path.suffix.lower() in {'.yaml','.yml'} else json.loads(text)

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def add(checks:list[dict], cid:str, ok:bool, evidence:Any):
    checks.append({'id':cid,'status':PASS if ok else FAIL,'evidence':evidence})

def text_files(root:Path):
    exts={'.md','.txt','.json','.yaml','.yml','.csv','.log','.sh','.py'}
    for p in root.rglob('*'):
        if p.is_file() and p.suffix.lower() in exts:
            yield p

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--package-dir', required=True)
    ap.add_argument('--policy', required=True)
    ap.add_argument('--report', required=True)
    ap.add_argument('--summary')
    a=ap.parse_args()
    root=Path(a.package_dir).resolve(); policy=load(Path(a.policy)); checks=[]
    if not root.is_dir():
        print('package-dir missing', file=sys.stderr); return 2

    required=policy.get('required_paths',[])
    missing=[x for x in required if not (root/x).exists()]
    add(checks,'required_paths',not missing,{'missing':missing})

    # Integrity: optional SHA256SUMS is enforced when present.
    sums=root/'SHA256SUMS.txt'; integrity_errors=[]
    if sums.exists():
        for line in sums.read_text(encoding='utf-8').splitlines():
            if not line.strip(): continue
            digest, rel=line.split(None,1); rel=rel.strip().lstrip('*')
            p=root/rel
            if not p.is_file() or sha256(p)!=digest: integrity_errors.append(rel)
    add(checks,'checksum_integrity',not integrity_errors,{'mismatches':integrity_errors,'manifest_present':sums.exists()})

    def safe(name, default):
        p=root/name
        try: return load(p) if p.exists() else default
        except Exception as e:
            add(checks,f'parse_{name}',False,{'error':str(e)}); return default
    selected=safe('selected_run.yaml',{}) or {}
    inventory=safe('artifact_inventory.json',{}) or {}
    receipts=safe('validator_receipts.json',{}) or {}
    driver=safe('driver_state.json',{}) or {}
    approvals=safe('approvals.json',{}) or {}

    artifacts=inventory.get('artifacts',[])
    types={x.get('type') for x in artifacts}
    req_types=set(policy.get('required_artifact_types',[]))
    missing_types=sorted(req_types-types)
    bad_paths=[]; invalid=[]; versions={}
    for art in artifacts:
        path=root/art.get('path','')
        if not path.is_file(): bad_paths.append(art.get('path'))
        if art.get('status') in {'invalidated','stale','rejected'}: invalid.append(art.get('id'))
        if art.get('type'): versions[art['type']]=art.get('version_id')
    add(checks,'artifact_inventory',not missing_types and not bad_paths and not invalid,{'missing_types':missing_types,'missing_paths':bad_paths,'invalid_artifacts':invalid})

    vr={x.get('artifact_type'):x for x in receipts.get('receipts',[])}
    validator_errors=[]
    for t in policy.get('mandatory_validators',[]):
        r=vr.get(t)
        if not r or r.get('status')!='PASS' or r.get('version_id')!=versions.get(t):
            validator_errors.append({'artifact_type':t,'receipt':r,'expected_version':versions.get(t)})
    add(checks,'mandatory_validator_receipts',not validator_errors,{'errors':validator_errors})

    # Selected-run consistency: canonical literals required; forbidden literals absent.
    canonical=selected.get('canonical_facts',{}) or {}
    canonical={k:(v.isoformat().replace('+00:00','Z') if hasattr(v,'isoformat') else v) for k,v in canonical.items()}
    forbidden=[str(x) for x in selected.get('forbidden_literals',[]) or []]
    consistency_errors=[]; foreign=[]
    for art in artifacts:
        p=root/art.get('path','')
        if not p.is_file(): continue
        text=p.read_text(encoding='utf-8',errors='replace')
        for key,val in canonical.items():
            if art.get('required_fact_keys') and key not in art['required_fact_keys']: continue
            if val is not None and str(val) not in text:
                consistency_errors.append({'artifact':art.get('id'),'fact':key,'expected':val})
        for lit in forbidden:
            if lit and lit in text: foreign.append({'artifact':art.get('id'),'literal':lit})
    add(checks,'selected_run_cross_artifact_consistency',not consistency_errors and not foreign,{'missing_canonical':consistency_errors,'foreign_literals':foreign})

    # Reference targets/current versions.
    refs=[]
    for art in artifacts:
        for ref in art.get('references',[]) or []:
            expected=versions.get(ref.get('artifact_type'))
            if ref.get('version_id')!=expected: refs.append({'artifact':art.get('id'),'reference':ref,'current':expected})
    add(checks,'current_version_references',not refs,{'stale_references':refs})

    # Manual QA contract.
    mqa=next((x for x in artifacts if x.get('type')=='manual_qa'),None)
    mqa_errors=[]
    if mqa and (root/mqa['path']).is_file():
        t=(root/mqa['path']).read_text(encoding='utf-8',errors='replace').lower()
        for n in policy['manual_qa']['required_steps']:
            if not re.search(rf'\bstep\s*{n}\b',t): mqa_errors.append(f'missing_step_{n}')
        for marker in policy['manual_qa']['required_markers']:
            if marker.lower() not in t: mqa_errors.append(f'missing_marker:{marker}')
    else: mqa_errors.append('manual_qa_missing')
    add(checks,'manual_qa_executable_completeness',not mqa_errors,{'errors':mqa_errors})

    auto=next((x for x in artifacts if x.get('type')=='automation'),None); auto_errors=[]
    if auto and (root/auto['path']).is_file():
        t=(root/auto['path']).read_text(encoding='utf-8',errors='replace').lower()
        for marker in policy['automation']['required_markers']:
            if marker.lower() not in t: auto_errors.append(f'missing_marker:{marker}')
    else: auto_errors.append('automation_missing')
    add(checks,'automation_completeness',not auto_errors,{'errors':auto_errors})

    # Approval binding and terminal state.
    app={x.get('artifact_type'):x for x in approvals.get('approvals',[])}; app_errors=[]
    for t in req_types:
        x=app.get(t)
        if not x or x.get('status')!='approved' or x.get('version_id')!=versions.get(t):
            app_errors.append({'artifact_type':t,'approval':x,'expected_version':versions.get(t)})
    add(checks,'approval_version_binding',not app_errors,{'errors':app_errors})
    status=driver.get('status'); complete=driver.get('complete') is True
    releasable_status=status in policy.get('releasable_driver_statuses',[])
    add(checks,'driver_terminal_releasable',complete and releasable_status,{'status':status,'complete':driver.get('complete')})

    claims=[]
    patterns=[re.compile(x) for x in policy.get('unsupported_claim_patterns',[])]
    for p in text_files(root/'artifacts') if (root/'artifacts').exists() else []:
        text=p.read_text(encoding='utf-8',errors='replace')
        for pat in patterns:
            if pat.search(text): claims.append({'path':str(p.relative_to(root)),'pattern':pat.pattern})
    add(checks,'unsupported_claims_absent',not claims,{'matches':claims})

    failed=[x for x in checks if x['status']==FAIL]
    terminal_fail=any(x['id']=='driver_terminal_releasable' for x in failed)
    disposition='PASS_RELEASE' if not failed else ('NO_GO' if terminal_fail else 'BLOCKED_REGENERATE')
    report={'schema_version':'ordo.benchmark.result_package_release_gate.report.v1','package_path':str(root),'checks':checks,'validated_versions':versions,'release_disposition':disposition,'releasable':not failed}
    canonical=json.dumps(report,ensure_ascii=False,sort_keys=True,separators=(',',':'),default=str).encode()
    report['report_sha256']=hashlib.sha256(canonical).hexdigest()
    out=Path(a.report); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+'\n',encoding='utf-8')
    if a.summary:
        lines=[f"Release disposition: {disposition}",f"Releasable: {not failed}",f"Checks: {len(checks)-len(failed)}/{len(checks)} PASS"]+[f"- FAIL {x['id']}" for x in failed]
        Path(a.summary).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(disposition)
    return 0 if not failed else 1
if __name__=='__main__': raise SystemExit(main())
