#!/usr/bin/env python3
from pathlib import Path
import argparse,re
from _alpha26_validation_common import source_program,update_paths,emit

def values_written(node):
 vals=[]
 def rec(v):
  if isinstance(v,dict):
   u=v.get('update_state')
   if isinstance(u,dict):
    for k,x in u.items(): vals.append((str(k),str(x)))
   for x in v.values(): rec(x)
  elif isinstance(v,list):
   for x in v: rec(x)
 rec(node); return vals

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package'); a=ap.parse_args(); root=Path(a.package); errors=[]
 p=source_program(root); nodes={str(x.get('id')):x for x in p.get('nodes') or [] if isinstance(x,dict) and x.get('id')}
 for g in p.get('gates') or []:
  if not isinstance(g,dict): continue
  cond=str(g.get('condition') or ''); op=g.get('on_pass'); targets=[op] if isinstance(op,str) else []
  for t in targets:
   n=nodes.get(t)
   if not n: continue
   for path,val in values_written(n):
    # gate requiring the exact post-pass value is inverted
    if val and re.search(rf'\b{re.escape(path)}\b\s*==\s*["\']?{re.escape(val)}["\']?',cond):
     errors.append(f'{g.get("id")}: requires post-pass value {path}={val} produced by {t}')
 return emit('VIBE_STATE_PHASE_ORDERING',errors)
if __name__=='__main__': raise SystemExit(main())
