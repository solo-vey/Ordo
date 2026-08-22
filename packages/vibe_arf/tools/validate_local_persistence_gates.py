#!/usr/bin/env python3
from pathlib import Path
import argparse,re
from _alpha26_validation_common import source_program,route_targets,update_paths,emit

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]; warnings=[]
 p=source_program(root); nodes={str(x.get('id')):x for x in p.get('nodes') or [] if isinstance(x,dict) and x.get('id')}; gates={str(x.get('id')):x for x in p.get('gates') or [] if isinstance(x,dict) and x.get('id')}
 for nid,n in nodes.items():
  paths=update_paths(n); approval=[x for x in paths if re.search(r'(^|\.)(approved|approval_ledger|approved_groups|proposal_reviews|human_decision)(\.|$)',x,re.I)]
  if not approval: continue
  targets=route_targets(n.get('on_answer'))
  gate_targets=[x for x in targets if x in gates]
  if not gate_targets: errors.append(f'{nid}: authority/apply state update lacks immediate deterministic persistence gate'); continue
  ok=False
  for gid in gate_targets:
   g=gates[gid]
   if str(g.get('trust_class') or '').lower()=='deterministic' or str(g.get('method') or '').lower() in {'deterministic','mechanical'}:
    cond=str(g.get('condition') or '')
    if any(x.split('.')[-1] in cond or x in cond for x in approval): ok=True
  if not ok: errors.append(f'{nid}: immediate gate does not verify persisted authority state')
 return emit('VIBE_LOCAL_PERSISTENCE_GATES',errors,warnings)
if __name__=='__main__': raise SystemExit(main())
