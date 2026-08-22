#!/usr/bin/env python3
from pathlib import Path
import argparse
from collections import defaultdict
from _alpha26_validation_common import load_yaml,emit

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]
 d=load_yaml(root/'authoring/approval_ledger.yaml')
 if d is None: return emit('VIBE_APPROVAL_PERSISTENCE',['approval_ledger missing'])
 if d.get('ledger_mode')!='append_only_revisioned': errors.append('ledger_mode must be append_only_revisioned')
 by=defaultdict(list)
 for i,e in enumerate(d.get('entries') or []):
  if not isinstance(e,dict): errors.append(f'entry[{i}] invalid'); continue
  gid=str(e.get('group_id') or ''); rev=e.get('revision')
  if not gid or not isinstance(rev,int) or rev<1: errors.append(f'entry[{i}]: group_id + positive integer revision required'); continue
  if set(e.get('approved_fields') or []) & set(e.get('rejected_fields') or []): errors.append(f'{gid}@{rev}: field both approved and rejected')
  if not e.get('authority'): errors.append(f'{gid}@{rev}: authority required')
  if not e.get('evidence'): errors.append(f'{gid}@{rev}: evidence required')
  by[gid].append(e)
 for gid,rows in by.items():
  revs=[x['revision'] for x in rows]
  if len(set(revs))!=len(revs): errors.append(f'{gid}: duplicate revisions')
  if revs!=sorted(revs): errors.append(f'{gid}: revisions must be monotonic')
  for prev,cur in zip(rows,rows[1:]):
   if cur.get('supersedes') not in {prev['revision'],str(prev['revision'])}: errors.append(f'{gid}@{cur["revision"]}: must supersede prior revision')
 return emit('VIBE_APPROVAL_PERSISTENCE',errors)
if __name__=='__main__': raise SystemExit(main())
