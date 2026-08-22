#!/usr/bin/env python3
from pathlib import Path
import argparse
from _alpha26_validation_common import load_json,emit

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]
 d=load_json(root/'reports/SIMULATION_EVIDENCE.json')
 if d is None: return emit('VIBE_SIMULATION_EVIDENCE',['reports/SIMULATION_EVIDENCE.json missing'])
 if str(d.get('status') or '').upper()!='PASS': errors.append(f'simulation status {d.get("status")}')
 for k in ['exact_candidate_sha256','kit_version','runtime_baseline']:
  if not d.get(k): errors.append(f'{k} required')
 if str(d.get('fixture_closure') or '').upper()!='PASS': errors.append('fixture_closure must PASS')
 if not d.get('scenarios'): errors.append('at least one executed scenario required')
 if int(d.get('profile_contract_gaps_count',0) or 0)!=0: errors.append('PASS simulation evidence cannot contain profile contract gaps')
 dep=load_json(root/'verification/SIMULATION_KIT_DEPENDENCY.json')
 if isinstance(dep,dict) and dep.get('version'):
  if str(d.get('kit_version'))!=str(dep.get('version')): errors.append(f'kit_version evidence {d.get("kit_version")} != pinned {dep.get("version")}')
  expected=str(dep.get('runtime_baseline') or '').replace('Ordo Tree Editor ','').strip()
  actual=str(d.get('runtime_baseline') or '').replace('Ordo Tree Editor ','').strip()
  if expected and actual and actual not in {expected,'policy-regression-proxy'}: errors.append(f'runtime_baseline evidence {d.get("runtime_baseline")} != pinned {dep.get("runtime_baseline")}')
 if d.get('acceptance_eligible') is True: errors.append('offline simulation evidence must not claim live acceptance eligibility')
 return emit('VIBE_SIMULATION_EVIDENCE',errors)
if __name__=='__main__': raise SystemExit(main())
