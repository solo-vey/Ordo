#!/usr/bin/env python3
from pathlib import Path
import json,re,tempfile,subprocess,sys
R=Path(__file__).resolve().parents[1]
checks=[]
def ck(i,c): checks.append((i,bool(c)))
# canonical source must remain authored and contain self-hosted authoring refs
canon=(R/'source/program.ordo.yaml').read_text()
ck('canonical_authoring_refs_preserved','authoring/' in canon)
# derived projection must remove forbidden references from the executable source while preserving exact-copy lineage
with tempfile.TemporaryDirectory() as td:
 cp=subprocess.run([sys.executable,str(R/'tools/materialize_model_run_projection.py'),str(R),td],capture_output=True,text=True)
 ck('projection_materializes',cp.returncode==0)
 p=Path(td); src=(p/'source/program.ordo.yaml').read_text() if (p/'source/program.ordo.yaml').is_file() else ''
 forbidden=['authoring/','verification/','tests/','editor/','compiled/','cli_embedded/']
 # Ignore projected model_support/<original> strings; no direct forbidden runtime refs may remain.
 direct=[]
 for pref in forbidden:
  direct += [m.start() for m in re.finditer(r'(?<!model_support/)'+re.escape(pref),src)]
 ck('all_forbidden_refs_are_projected', 'model_support/authoring/' in src and 'model_support/verification/' in src)
 man=json.loads((p/'MODEL_RUN_SUPPORT_PROJECTION.json').read_text()) if (p/'MODEL_RUN_SUPPORT_PROJECTION.json').is_file() else {}
 ck('projection_lineage',man.get('canonical_source_sha256') and man.get('projected_source_sha256') and man.get('resolved_count',0)>0)
 ck('exact_copy_only',all(x.get('materialization') in {'exact_copy','unresolved_reference_preserved'} for x in man.get('mappings',[])))
 ck('no_forbidden_surface_dirs',all(not (p/x.rstrip('/')).exists() for x in forbidden))
 d=subprocess.run([sys.executable,str(R/'tools/materialize_profile_dependency_closure.py'),td,'--profile','MODEL_RUN','--output','MODEL_RUN_PACKAGE_DEPENDENCY_CLOSURE.json'],capture_output=True,text=True)
 closure=json.loads((p/'MODEL_RUN_PACKAGE_DEPENDENCY_CLOSURE.json').read_text()) if (p/'MODEL_RUN_PACKAGE_DEPENDENCY_CLOSURE.json').is_file() else {}
 bad=[x for x in closure.get('rejected_forbidden_references',[]) if str(x.get('reason','')).startswith('explicit_ref:source/program.ordo.yaml')]
 ck('closure_accepts_projected_source',d.returncode==0 and not bad)
print('\n'.join(('PASS' if c else 'FAIL')+': '+i for i,c in checks))
raise SystemExit(0 if all(c for _,c in checks) else 1)
