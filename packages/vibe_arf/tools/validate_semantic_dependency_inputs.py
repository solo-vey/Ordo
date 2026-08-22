#!/usr/bin/env python3
from pathlib import Path
import argparse
from _alpha26_validation_common import source_program,emit

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]
 p=source_program(root)
 for n in p.get('nodes') or []:
  if not isinstance(n,dict) or not n.get('id'): continue
  inputs=set(str(x) for x in (n.get('inputs') or [])); ac=n.get('authority_contract') or {}
  for d in ac.get('derived_targets') or []:
   if not isinstance(d,dict): continue
   for s in d.get('sources') or []:
    if str(s) not in inputs: errors.append(f'{n["id"]}: authority source {s} not declared in inputs')
 return emit('VIBE_SEMANTIC_DEPENDENCY_INPUTS',errors)
if __name__=='__main__': raise SystemExit(main())
