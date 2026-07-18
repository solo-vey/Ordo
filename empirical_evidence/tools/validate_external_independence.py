#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
try:
 import jsonschema
except ImportError:
 jsonschema=None
LEVELS=['self_declared_independence_unverified','timestamp_verified','public_release_bound_verified','organizationally_separated','third_party_verified']
REQUIRED={
 'self_declared_independence_unverified':{'completed_declaration','original_package_sha256','author_assistance_declaration'},
 'timestamp_verified':{'trusted_timestamp_proof'},
 'public_release_bound_verified':{'public_release_binding','no_internal_package_use_declaration'},
 'organizationally_separated':{'organizational_separation_attestation','no_internal_repository_access_declaration','no_direct_author_participation_declaration'},
 'third_party_verified':{'third_party_verification_record'},
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def evidence_present(case):
 return {e['evidence_type'] for e in case['independence_verification'].get('evidence_records',[]) if e['status']=='present'}
def required_for(level):
 req=set()
 for name in LEVELS[:LEVELS.index(level)+1]: req |= REQUIRED[name]
 return req
def validate_case(case_path:Path,schema_path:Path|None=None):
 issues=[]; case=json.loads(case_path.read_text())
 if schema_path and jsonschema:
  try: jsonschema.validate(case,json.loads(schema_path.read_text()))
  except Exception as exc: issues.append(f"schema failure: {getattr(exc,'message',str(exc))}")
 if issues: return {'status':'blocked','issues':issues}
 iv=case['independence_verification']; level=iv['declared_level']; present=evidence_present(case)
 missing=sorted(required_for(level)-present)
 if missing: issues.append('declared independence level lacks required evidence: '+', '.join(missing))
 if level=='self_declared_independence_unverified' and iv['claim_status']!='unverified_self_declaration': issues.append('self-declared level must use unverified_self_declaration claim status')
 if level!='self_declared_independence_unverified' and iv['claim_status']!='evidence_supported': issues.append('verified levels require evidence_supported claim status')
 access=iv['internal_access']
 if level in ('organizationally_separated','third_party_verified') and any(access[k]!='no' for k in access): issues.append('organizational separation requires explicit no for all internal access fields')
 claim=case.get('bounded_claim','').lower()
 if level=='self_declared_independence_unverified' and (('verified independent' in claim and 'not verified independent' not in claim) or ('independently verified' in claim and 'not independently verified' not in claim)): issues.append('bounded claim overstates unverified independence')
 sh=case['source_handling']; root=case_path.parent
 pkg=root/sh['publication_safe_package']
 if not pkg.is_file(): issues.append('missing publication-safe package')
 elif sha(pkg)!=sh['publication_safe_package_sha256']: issues.append('publication-safe package checksum mismatch')
 if sh['original_specific_source_included'] is not False or sh['original_package_identity']['confidential_source_publicly_included'] is not False: issues.append('confidential original source must not be included publicly')
 return {'schema_version':'ordo.empirical_evidence.independence_validation_report.v1','case_id':case.get('case_id'),'declared_level':level,'supported_level':level if not missing else 'self_declared_independence_unverified','status':'passed' if not issues else 'blocked','issues':issues}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('case',type=Path); ap.add_argument('--schema',type=Path); ap.add_argument('--out',type=Path); a=ap.parse_args(); r=validate_case(a.case,a.schema); txt=json.dumps(r,indent=2)+'\n'; a.out.write_text(txt) if a.out else print(txt,end=''); return 0 if r['status']=='passed' else 1
if __name__=='__main__': raise SystemExit(main())
