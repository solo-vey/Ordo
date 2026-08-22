#!/usr/bin/env python3
from pathlib import Path
import json, yaml, sys, tempfile, subprocess, shutil, importlib.util
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from pattern_template_semantics import execution_components, canonical_outcome_edges
from pattern_data_layer_semantics import data_roles
from instantiate_data_layer_pattern import build

fail=[]; passed=0
def ck(ok,msg):
 global passed
 if ok: passed+=1
 else: fail.append(msg)

reg=json.loads((ROOT/'patterns/PATTERN_REGISTRY.json').read_text())
rows={p['id']:p for p in reg.get('patterns',[])}
expected={
 'SIMPLE_DOCUMENT_RECONCILIATION_VERIFICATION':'1.2',
 'SIMPLE_VERIFIED_DOCUMENT_CODE_IMPLEMENTATION':'1.1',
}
for pid,ver in expected.items():
 r=rows.get(pid,{})
 ck(str(r.get('version'))==ver,f'{pid}: registry version mismatch')
 ck(r.get('selection_match_policy')=='capability_required',f'{pid}: must require semantic capability match')
 ck(r.get('variant_tier')=='simple',f'{pid}: simple variant metadata missing')
 base=ROOT/'patterns'/pid
 for fn in ('PATTERN.yaml','DATA_LAYER.template.yaml','EXECUTION.template.yaml','COMPILATION_CONTRACT.md','DOMAIN_BINDINGS.template.yaml'):
  ck((base/fn).exists(),f'{pid}: missing {fn}')
 pdef=yaml.safe_load((base/'PATTERN.yaml').read_text()) or {}
 ident=pdef.get('pattern') or {}
 ck(ident.get('id')==pid and str(ident.get('version'))==ver,f'{pid}: authoritative identity mismatch')
 ex=yaml.safe_load((base/'EXECUTION.template.yaml').read_text()) or {}
 comps=execution_components(ex); edges=canonical_outcome_edges(ex)
 ck(bool(comps),f'{pid}: execution responsibilities empty after dialect normalization')
 ck(bool(edges),f'{pid}: canonical outcomes empty')
 roles={x.get('role') for x in comps}
 ck(all(e.get('from_role') in roles for e in edges),f'{pid}: unresolved edge source')
 ck(all(e.get('to_role') in roles or e.get('terminal') for e in edges),f'{pid}: unresolved edge destination')
 ck(all(e.get('outcome') for e in edges),f'{pid}: missing exact outcome token')
 dl=yaml.safe_load((base/'DATA_LAYER.template.yaml').read_text()) or {}
 ck(isinstance(data_roles(dl),list) and bool(data_roles(dl)),f'{pid}: Data Layer dialect not normalized')
 # generator can create an instance object without inventing domain bindings
 inst=build(ROOT,pid,'TEST_'+pid,{},None,selection_status='explicit_variant_test',requirement_origin='test_preexisting_requirement')
 ck(inst.get('pattern_id')==pid and inst.get('instance_digest'),f'{pid}: generator instance build failed')

# Advanced variants must still coexist at their previous versions.
ck(str(rows.get('DOCUMENT_RECONCILIATION_VERIFICATION',{}).get('version'))=='1.2','advanced reconciliation missing/changed')
ck(str(rows.get('VERIFIED_DOCUMENT_CODE_IMPLEMENTATION',{}).get('version'))=='1.2','advanced code implementation missing/changed')
ck(reg.get('variant_selection_policy',{}).get('multiple_matching_variants_require_explicit_choice') is True,'explicit variant-choice policy missing')

# Exact SIMPLE semantics.
rec=yaml.safe_load((ROOT/'patterns/SIMPLE_DOCUMENT_RECONCILIATION_VERIFICATION/EXECUTION.template.yaml').read_text()) or {}
redges=canonical_outcome_edges(rec)
ck(any(e.get('outcome')=='NO_QUESTIONS' for e in redges),'simple reconciliation clean branch missing')
ck(any(e.get('outcome')=='QUESTIONS_REQUIRED' for e in redges),'simple reconciliation analyst branch missing')
ck(any(e.get('to_role')=='reconcile_and_build_questions' and e.get('from_role')=='apply_authority_resolutions' for e in redges),'simple reconciliation loop missing')
text=(ROOT/'patterns/SIMPLE_DOCUMENT_RECONCILIATION_VERIFICATION/PATTERN.yaml').read_text()
ck('no independent-review/multi-stage-repair tree' not in text.lower(), 'unexpected prose sentinel') # structure checked below
ck('independent_review' not in {x.get('role') for x in execution_components(rec)},'simple reconciliation accidentally gained independent review')

code=yaml.safe_load((ROOT/'patterns/SIMPLE_VERIFIED_DOCUMENT_CODE_IMPLEMENTATION/EXECUTION.template.yaml').read_text()) or {}
cedges=canonical_outcome_edges(code)
scope={e.get('outcome') for e in cedges if e.get('from_role')=='local_scope_gate'}
ck(scope=={'LOCAL_SAFE','HANDOFF_REQUIRED'},f'simple code scope outcomes changed: {scope}')
ck(any(e.get('outcome')=='HANDOFF_REQUIRED' and e.get('terminal')=='HANDOFF_REQUIRED' for e in cedges),'handoff terminal missing')
ck(any(e.get('outcome')=='FAIL' and e.get('terminal')=='IMPLEMENTATION_BLOCKED' for e in cedges),'implementation blocked terminal missing')
ck(len(execution_components(code))==8,'simple code v1.1 must remain compact at exactly eight responsibilities (freshness pair + original simple flow)')

# Reconciliation facet metadata must follow authoritative PATTERN v1.2.
dlrec=yaml.safe_load((ROOT/'patterns/SIMPLE_DOCUMENT_RECONCILIATION_VERIFICATION/DATA_LAYER.template.yaml').read_text()) or {}
ck(str(dlrec.get('pattern_version'))=='1.2','simple reconciliation Data Layer facet version not aligned to authoritative PATTERN 1.2')

print(json.dumps({'status':'PASS' if not fail else 'FAIL','passed':passed,'failed':len(fail),'failures':fail},indent=2))
raise SystemExit(1 if fail else 0)
