#!/usr/bin/env python3
from pathlib import Path
import argparse
from _alpha26_validation_common import load_json,emit

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]
 d=load_json(root/'reports/RUNTIME_GATE_EVIDENCE.json')
 # Self factory may qualify the invariant through regression rather than executing itself as a generated target.
 if d is None: return emit('VIBE_RUNTIME_GATE_EVIDENCE',['reports/RUNTIME_GATE_EVIDENCE.json missing'])
 for i,g in enumerate(d.get('gates') or []):
  if str(g.get('status') or '').upper()=='PASS' and (not g.get('check_results') or not g.get('evidence')):
   errors.append(f'gate[{i}] {g.get("gate_id")}: PASS is vacuous')
 return emit('VIBE_RUNTIME_GATE_EVIDENCE',errors)
if __name__=='__main__': raise SystemExit(main())
