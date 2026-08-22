#!/usr/bin/env python3
from pathlib import Path
import argparse
from _alpha26_validation_common import load_json,emit
ALLOWED={'ORDO_LANGUAGE_INVALID','PLAYBOOK_SOURCE_CONTRACT_DEFECT','VERIFIER_COMPILER_PARITY_DEFECT','SIMULATION_FIXTURE_INCOMPLETE','MODEL_QUALITY_DEFECT','RUNTIME_ADAPTER_CONFORMANCE_DEFECT','EDITOR_UI_TOOLING_DEFECT'}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]
 d=load_json(root/'reports/DEFECT_OWNERSHIP.json')
 if d is None: return emit('VIBE_DEFECT_OWNERSHIP',['reports/DEFECT_OWNERSHIP.json missing'])
 for i,f in enumerate(d.get('findings') or []):
  if f.get('primary_owner') not in ALLOWED: errors.append(f'finding[{i}]: invalid/missing primary_owner')
  if not f.get('evidence'): errors.append(f'finding[{i}]: evidence required')
  if f.get('primary_owner')=='RUNTIME_ADAPTER_CONFORMANCE_DEFECT' and f.get('playbook_workaround_applied') is True: errors.append(f'finding[{i}]: runtime defect must not create playbook workaround')
 return emit('VIBE_DEFECT_OWNERSHIP',errors)
if __name__=='__main__': raise SystemExit(main())
