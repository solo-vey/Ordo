#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,sys
R=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve(); errs=[]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
try: pol=json.loads((R/'source/data-layer-first-hard-architecture-policy.json').read_text())
except Exception as e: pol={}; errs.append({'code':'POLICY_LOAD','detail':str(e)})
if pol.get('authoring_source_of_truth')!='data_layer': errs.append({'code':'CANONICAL_SOURCE_INVALID'})
if pol.get('direct_graph_or_source_semantic_edit')!='forbidden': errs.append({'code':'DIRECT_EDIT_NOT_FORBIDDEN'})
mp=R/'authoring/projection_generation_manifest.json'; m={}
if not mp.exists(): errs.append({'code':'LINEAGE_MANIFEST_MISSING'})
else:
 try: m=json.loads(mp.read_text())
 except Exception as e: errs.append({'code':'LINEAGE_MANIFEST_INVALID','detail':str(e)})
 for rel,old in (m.get('upstream_hashes') or {}).items():
  p=R/rel
  if not p.exists() or sha(p)!=old: errs.append({'code':'UPSTREAM_STALE','path':rel})
 for rel,old in (m.get('intermediate_hashes') or {}).items():
  p=R/rel
  if not p.exists() or sha(p)!=old: errs.append({'code':'DERIVED_INTERMEDIATE_STALE','path':rel})
 for rel,old in (m.get('downstream_hashes') or {}).items():
  p=R/rel
  if not p.exists() or sha(p)!=old: errs.append({'code':'DOWNSTREAM_DIRECT_EDIT','path':rel})
 expected=set(pol.get('canonical_upstream_files') or []); actual=set((m.get('upstream_hashes') or {}).keys())
 for x in sorted(expected-actual): errs.append({'code':'UPSTREAM_LINEAGE_MISSING','path':x})
 expected_i=set(pol.get('derived_intermediate_files') or []); actual_i=set((m.get('intermediate_hashes') or {}).keys())
 for x in sorted(expected_i-actual_i): errs.append({'code':'INTERMEDIATE_LINEAGE_MISSING','path':x})
 expected_d=set(pol.get('downstream_projection_files') or []); actual_d=set((m.get('downstream_hashes') or {}).keys())
 for x in sorted(expected_d-actual_d): errs.append({'code':'DOWNSTREAM_LINEAGE_MISSING','path':x})
out={'schema_version':'1.1','validator':'VIBE_DATA_LAYER_FIRST_HARD_ARCHITECTURE','status':'PASS' if not errs else 'FAIL','errors':errs}; print(json.dumps(out,indent=2)); sys.exit(0 if not errs else 1)
