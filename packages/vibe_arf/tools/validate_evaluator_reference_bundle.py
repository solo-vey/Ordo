#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path

def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('package_root'); ap.add_argument('--manifest',default='evaluator/reference_bundle/manifest.json'); a=ap.parse_args(); root=Path(a.package_root).resolve(); mp=root/a.manifest
 if not mp.is_file(): print(json.dumps({'status':'FAIL','code':'MANIFEST_MISSING'})); return 2
 d=json.loads(mp.read_text()); errors=[]
 if d.get('access_scope')!='evaluator_only': errors.append('ACCESS_SCOPE')
 if d.get('allowed_consumers')!=['comparative_evaluator']: errors.append('ALLOWLIST')
 if set(d.get('denied_consumers',[]))!={'generator','optimizer'}: errors.append('DENYLIST')
 if not d.get('references'): errors.append('EMPTY_REFERENCE_SET')
 for r in d.get('references',[]):
  p=(root/r.get('bundle_path','')).resolve()
  if root not in p.parents or not p.is_file(): errors.append('REFERENCE_FILE_MISSING'); continue
  if h(p)!=r.get('sha256'): errors.append('REFERENCE_HASH_MISMATCH')
  if r.get('access_scope')!='evaluator_only': errors.append('REFERENCE_SCOPE')
 print(json.dumps({'status':'PASS' if not errors else 'FAIL','errors':errors,'reference_count':len(d.get('references',[]))}))
 return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
