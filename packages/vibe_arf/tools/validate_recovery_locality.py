#!/usr/bin/env python3
from pathlib import Path
import argparse,re
from _alpha26_validation_common import source_program,emit

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]; warnings=[]
 p=source_program(root); entry=str((p.get('graph_contract') or {}).get('entry_node') or '')
 for g in p.get('gates') or []:
  if not isinstance(g,dict): continue
  fail=g.get('on_fail') or g.get('fail_to')
  gid=str(g.get('id') or '')
  if isinstance(fail,str):
   if entry and fail==entry and not re.search(r'global|startup|package|final',gid,re.I): errors.append(f'{gid}: broad recovery to entry {entry}')
   if re.search(r'RETURN_TO_STAGE|START_OVER|RESTART',fail,re.I): warnings.append(f'{gid}: generic recovery target {fail}; require explicit causal justification')
 return emit('VIBE_RECOVERY_LOCALITY',errors,warnings)
if __name__=='__main__': raise SystemExit(main())
