#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
try:
 import jsonschema
except ImportError:
 jsonschema=None
SCHEMA_BY_VERSION={
 "ordo.empirical_evidence.task_class.v1":"task_class.schema.json",
 "ordo.empirical_evidence.case.v1":"case.schema.json",
 "ordo.empirical_evidence.run.v1":"run.schema.json",
 "ordo.empirical_evidence.scorecard.v1":"scorecard.schema.json",
 "ordo.empirical_evidence.finding.v1":"finding.schema.json",
 "ordo.empirical_evidence.claim.v1":"claim.schema.json",
 "ordo.empirical_evidence.admission.v1":"admission.schema.json",
 "ordo.empirical_evidence.envelope.v1":"evidence_envelope.schema.json",
 "ordo.empirical_evidence.external_adoption_case.v1":"external_adoption_case.schema.json",
 "ordo.empirical_evidence.external_adoption_case.v2":"external_adoption_case.schema.json",
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(root:Path):
 issues=[]; checked=0
 registry=json.loads((root/'manifests/SCHEMA_REGISTRY.json').read_text())
 for e in registry['schemas']:
  if not (root/e['path']).is_file(): issues.append(f"missing schema: {e['path']}")
 index=json.loads((root/'manifests/EMPIRICAL_EVIDENCE_INDEX.json').read_text())
 if index.get('raw_evidence_policy')!='immutable': issues.append('raw evidence policy must be immutable')
 if index.get('existing_evaluation_relationship')!='independent_parallel': issues.append('evaluation relationship must remain independent_parallel')
 for layer in ['task_classes','cases','runs','scorecards','findings','claims','admissions','external_adoption_cases']:
  for rel in index.get(layer,[]):
   p=root/rel
   if not p.is_file(): issues.append(f"missing indexed artifact: {rel}"); continue
   obj=json.loads(p.read_text()); checked+=1
   version=obj.get('schema_version'); schema_name=SCHEMA_BY_VERSION.get(version)
   if not schema_name: issues.append(f"unknown schema_version in {rel}: {version}"); continue
   if jsonschema: 
    try: jsonschema.validate(obj,json.loads((root/'schemas'/schema_name).read_text()))
    except Exception as exc: issues.append(f"schema failure {rel}: {exc.message if hasattr(exc,'message') else exc}")

   if layer=='external_adoption_cases':
    from validate_external_independence import validate_case
    ivr=validate_case(p,root/'schemas/external_adoption_case.schema.json')
    issues.extend([f"independence validation {obj.get('case_id')}: {x}" for x in ivr['issues']])
    sh=obj['source_handling']; pkg=root/Path(rel).parent/sh['publication_safe_package']
    if not pkg.is_file(): issues.append(f"missing publication-safe package: {pkg.relative_to(root)}")
    elif sha(pkg)!=sh['publication_safe_package_sha256']: issues.append(f"publication-safe package checksum mismatch: {obj['case_id']}")
    if sh.get('original_specific_source_included') is not False: issues.append(f"original specific source must be excluded: {obj['case_id']}")
   if layer=='runs':
    raw=root/obj['raw_evidence']['path']
    if not raw.is_file(): issues.append(f"missing raw evidence: {obj['raw_evidence']['path']}")
    elif sha(raw)!=obj['raw_evidence']['sha256']: issues.append(f"raw evidence checksum mismatch: {obj['run_id']}")
 return {'schema_version':'ordo.empirical_evidence.validation_report.v1','status':'passed' if not issues else 'blocked','checked_artifacts':checked,'issues':issues}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('root',type=Path); ap.add_argument('--out',type=Path); a=ap.parse_args(); r=validate(a.root); text=json.dumps(r,indent=2)+'\n'; a.out.write_text(text) if a.out else print(text,end=''); return 0 if r['status']=='passed' else 1
if __name__=='__main__': raise SystemExit(main())
