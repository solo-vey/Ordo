#!/usr/bin/env python3
from pathlib import Path
import argparse,re
from _alpha26_validation_common import load_yaml,source_program,emit

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]; warnings=[]
 cfg=load_yaml(root/'authoring/proposal_canonicalization.yaml')
 if cfg is None: return emit('VIBE_PROPOSAL_CANONICAL_SEPARATION',['proposal_canonicalization missing'])
 roots=[str(cfg.get(k) or '') for k in ['proposal_state_root','approved_projection_root','canonical_state_root']]
 if any(not x for x in roots): errors.append('proposal/approved_projection/canonical roots are required')
 if len(set(roots))!=3: errors.append('proposal, approved_projection and canonical roots must be distinct')
 rules=cfg.get('rules') or {}
 if rules.get('deep_merge_proposal_into_canonical_forbidden') is not True: errors.append('deep merge proposal->canonical must be forbidden')
 if rules.get('materializers_must_consume_approved_projection') is not True: errors.append('materializers must consume approved projection')
 prog=source_program(root)
 prop,approved,canon=roots if len(roots)==3 else ('proposal','approved_projection','canonical')
 # Heuristic guard over executable state writes only: canonical destinations may not read directly from proposal roots.
 def walk(v):
  if isinstance(v,dict):
   u=v.get('update_state')
   if isinstance(u,dict):
    for k,x in u.items():
     if str(k).startswith(canon) and prop in str(x): errors.append(f'direct proposal->canonical write: {k}')
   for x in v.values(): walk(x)
  elif isinstance(v,list):
   for x in v: walk(x)
 walk(prog.get('nodes') or [])
 return emit('VIBE_PROPOSAL_CANONICAL_SEPARATION',errors,warnings)
if __name__=='__main__': raise SystemExit(main())
