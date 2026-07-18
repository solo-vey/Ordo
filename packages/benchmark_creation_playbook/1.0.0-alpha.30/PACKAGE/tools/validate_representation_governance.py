#!/usr/bin/env python3
import argparse,json,pathlib,sys

def validate(root,candidate):
 reg=json.loads((root/'REPRESENTATION_REGISTRY.json').read_text())
 c=json.loads(candidate.read_text())
 errs=[]
 rid=c.get('representation_id'); profile=reg['representations'].get(rid)
 if not profile: errs.append('UNREGISTERED_REPRESENTATION'); return errs
 if c.get('source_type') not in profile['allowed_source_types']: errs.append('UNAUTHORIZED_SOURCE_TYPE')
 if c.get('strategy')!=profile['strategy']: errs.append('UNAUTHORIZED_TRANSFORMATION_STRATEGY')
 if not c.get('lineage_complete'): errs.append('INCOMPLETE_LINEAGE')
 if not c.get('semantic_parity_pass'): errs.append('SEMANTIC_PARITY_FAILURE')
 inv=c.get('invariants',{})
 missing=[x for x in reg['common_invariants'] if inv.get(x) is not True]
 if missing: errs.append('COMMON_INVARIANT_FAILURE:'+','.join(missing))
 files='\n'.join(c.get('external_files',[])).lower()
 if rid=='MIXED_ACCUMULATED_INSTRUCTIONS':
  forbidden=['yaml','compiler','provenance','benchmark_metadata','node_mapping','expected_route']
  hit=[x for x in forbidden if x in files]
  if hit or not c.get('disclosure_isolation_pass'): errs.append('FORBIDDEN_DISCLOSURE')
 if rid=='DOMAIN_ADAPTED_ALL_IN_ONE' and not c.get('domain_source_present'): errs.append('MISSING_ACTUAL_DOMAIN_SOURCE')
 return errs

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--root',type=pathlib.Path,required=True); ap.add_argument('--candidate',type=pathlib.Path,required=True); ap.add_argument('--report',type=pathlib.Path)
 a=ap.parse_args(); errs=validate(a.root,a.candidate); report={'status':'PASS' if not errs else 'FAIL','errors':errs,'failure_terminal':None if not errs else 'NO_CHANGE / REPRESENTATION_COMPILATION_GOVERNANCE_FAILURE'}
 text=json.dumps(report,indent=2); print(text)
 if a.report: a.report.write_text(text+'\n')
 return 0 if not errs else 2
if __name__=='__main__': raise SystemExit(main())
