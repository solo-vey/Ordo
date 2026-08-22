#!/usr/bin/env python3
from pathlib import Path
import argparse
from _alpha26_validation_common import load_yaml,load_json,emit

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]
 m=load_yaml(root/'authoring/scenario_matrix.yaml')
 if m is None: return emit('VIBE_BEHAVIORAL_SCENARIO_COVERAGE',['scenario_matrix missing'])
 req=set(m.get('required_families') or []); covered=set(); ids=set()
 for s in m.get('scenarios') or []:
  if not isinstance(s,dict) or not s.get('id'): continue
  ids.add(str(s['id'])); covered.update(str(x) for x in (s.get('families') or []))
 miss=sorted(req-covered)
 if miss: errors.append(f'missing scenario families: {miss}')
 ev=load_json(root/'reports/SIMULATION_EVIDENCE.json')
 if ev is not None and str(ev.get('status') or '').upper()=='PASS':
  passed={str(x.get('id')) for x in ev.get('scenarios') or [] if isinstance(x,dict) and str(x.get('status') or '').upper()=='PASS'}
  if ids and not ids.issubset(passed): errors.append(f'designed scenarios not proven PASS: {sorted(ids-passed)}')
 return emit('VIBE_BEHAVIORAL_SCENARIO_COVERAGE',errors,extra={'required_families':sorted(req),'covered_families':sorted(covered)})
if __name__=='__main__': raise SystemExit(main())
