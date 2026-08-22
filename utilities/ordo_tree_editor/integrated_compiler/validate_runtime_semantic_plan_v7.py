#!/usr/bin/env python3
import argparse,json,sys,re
from pathlib import Path

def _source_location(plan, element_id):
 source=(plan.get('source') or {}).get('program')
 if not source or not element_id:
  return {'file':source or None,'line':None,'column':None}
 path=Path(source)
 try:
  text=path.read_text(encoding='utf-8')
 except Exception:
  return {'file':source,'line':None,'column':None}
 # Best-effort source location: exact scalar occurrence of the element id.
 patterns=[f'id: {element_id}',f'id: "{element_id}"',f"id: '{element_id}'",element_id+':']
 for lineno,line in enumerate(text.splitlines(),1):
  for pattern in patterns:
   idx=line.find(pattern)
   if idx>=0:
    return {'file':source,'line':lineno,'column':idx+1}
 return {'file':source,'line':None,'column':None}

def _diagnostic_from_compiler_issue(plan, issue):
 code=str(issue.get('code') or 'COMPILER_ISSUE')
 eid=issue.get('element_id')
 els=plan.get('elements') or {}
 element=els.get(eid) if eid else None
 routes=[]
 if isinstance(element,dict):
  for route in element.get('routes') or []:
   if isinstance(route,dict):
    routes.append({'label':route.get('label') or route.get('outcome') or route.get('when'),'target':route.get('target')})
 title=code.replace('_',' ').title()
 message=str(issue.get('message') or issue.get('detail') or '')
 expected='Compiler/runtime semantic invariant must be satisfied.'
 remediation='Review the affected source element and correct the reported invariant before starting the playbook.'
 if code=='GRAPH_NOT_FULLY_REACHABLE':
  title='Graph is not fully reachable'
  missing=issue.get('unreachable') or []
  message=f"{len(missing)} element(s) cannot be reached from the declared entry node: {', '.join(map(str,missing))}."
  expected='Every executable element must be reachable from graph_contract.entry_node through valid control-flow routes.'
  remediation='Connect each unreachable element to an intended control-flow branch, or remove it if it is not executable.'
 elif code=='NONTERMINAL_WITHOUT_ROUTE':
  title='Non-terminal element has no outgoing route'
  message=f"{eid} is not terminal but the compiled element has no valid outgoing route."
  expected='Every non-terminal node or gate must have at least one valid outgoing route to another element or allowed external terminal target.'
  remediation='Add the intended next/on_pass/on_fail/on_answer transition in the source, or mark the element terminal if it should end execution.'
 loc=_source_location(plan,eid)
 return {
  'severity':issue.get('severity') or 'error','code':code,'title':title,'message':message,
  'element_id':eid,'element_kind':element.get('kind') if isinstance(element,dict) else None,
  'current_routes':routes,'unreachable':issue.get('unreachable') or [],
  'reachable':issue.get('reachable'),'total':issue.get('total'),'path':issue.get('path'),
  'source_location':loc,'expected':expected,'remediation':remediation,'compiler_issue':issue,
 }

def _diagnostic_from_message(plan, category, message):
 text=str(message)
 eid=None
 m=re.search(r'\b(?:N|G|D|END)_[A-Z0-9_]+\b',text)
 if m: eid=m.group(0)
 return {
  'severity':'error','code':'VALIDATION_'+category.upper(),'title':category.title()+' validation issue',
  'message':text,'element_id':eid,'element_kind':((plan.get('elements') or {}).get(eid) or {}).get('kind') if eid else None,
  'current_routes':copy_routes(plan,eid),'source_location':_source_location(plan,eid),
  'expected':'The runtime semantic plan must satisfy the validator invariant represented by this diagnostic.',
  'remediation':'Inspect this diagnostic together with the affected source element and correct the underlying playbook/compiler contract violation.',
 }

def copy_routes(plan,eid):
 element=(plan.get('elements') or {}).get(eid) if eid else None
 if not isinstance(element,dict): return []
 return [{'label':r.get('label') or r.get('outcome') or r.get('when'),'target':r.get('target')} for r in (element.get('routes') or []) if isinstance(r,dict)]

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('plan'); args=ap.parse_args(); p=json.loads(Path(args.plan).read_text())
 structural=[]; semantic=[]
 if p.get('format')!='ordo.runtime_semantic_plan': structural.append('wrong format')
 rc=p.get('runtime_execution_contract') or {}
 if rc.get('instruction_assembler')!='runtime_semantic_v1': structural.append('runtime semantic instruction assembler contract missing')
 if not str(p.get('format_version','')).startswith('1.4'): structural.append('wrong format_version')
 els=p.get('elements') or {}; ids=set(els); entry=(p.get('graph') or {}).get('entry_node')
 if entry not in ids: structural.append(f'entry node missing: {entry}')
 ext_targets=set((p.get('graph') or {}).get('external_terminal_targets') or [])
 # Internal graph reachability is a blocking structural invariant.
 edges={eid:{r.get('target') for r in (e.get('routes') or []) if r.get('target') in ids} for eid,e in els.items()}
 if entry in ids:
  seen={entry}; stack=[entry]
  while stack:
   x=stack.pop()
   for y in edges.get(x,set()):
    if y not in seen: seen.add(y); stack.append(y)
  if seen!=ids: structural.append(f'graph not fully reachable: {len(seen)}/{len(ids)}; missing={sorted(ids-seen)}')
 for eid,e in els.items():
  if e.get('id')!=eid: structural.append(f'{eid}: id mismatch')
  if not isinstance(e.get('semantic_source'),dict): structural.append(f'{eid}: semantic_source missing')
  sc=e.get('state_contract') or {}
  if 'writes' not in sc: structural.append(f'{eid}: writes missing')
  if 'output_contract' not in e: structural.append(f'{eid}: output_contract missing')
  for r in e.get('routes') or []:
   t=r.get('target')
   if t not in ids and t not in ext_targets: structural.append(f'{eid}: route target not found: {t}')
  if e.get('kind','').endswith('_gate') and 'gate_contract' not in e: structural.append(f'{eid}: gate_contract missing')
  # Fidelity is structural preservation in V7.1: exact key-set fingerprint must agree.
  sf=e.get('semantic_fidelity') or {}; src=e.get('semantic_source') or {}
  if sorted(src.keys()) != sorted(sf.get('source_keys') or []): semantic.append(f'{eid}: semantic source key loss')
  # Human gates must retain criterion.
  if e.get('kind')=='human_gate' and not (e.get('analyst_interaction') or {}).get('criterion'): semantic.append(f'{eid}: human gate criterion missing')
  # Gate result contract must be representable.
  if e.get('kind','').endswith('_gate'):
   oc=e.get('output_contract') or {}
   if oc.get('contract')!='GateFailureOrPass': semantic.append(f'{eid}: gate-specific output contract missing')
   gc=e.get('gate_contract') or {}; rc=gc.get('result_contract')
   if isinstance(rc,dict) and rc.get('required_output') and not gc.get('external_specification') and not gc.get('checks_inline'):
    semantic.append(f'{eid}: result contract exists but semantic gate specification is unavailable')
  else:
   if (e.get('output_contract') or {}).get('contract')!='NodeExecutionResult': semantic.append(f'{eid}: node-specific output contract missing')
   writes=set(sc.get('writes') or [])
   item=((((e.get('output_contract') or {}).get('state_patch') or {}).get('operations') or {}).get('items') or {})
   enum=set((item.get('properties') or {}).get('path',{}).get('enum') or [])
   if not enum and isinstance(item.get('anyOf'),list):
    for variant in item.get('anyOf') or []:
     path_schema=((variant.get('properties') or {}).get('path') or {}) if isinstance(variant,dict) else {}
     if 'const' in path_schema: enum.add(str(path_schema.get('const')))
     enum.update(str(x) for x in (path_schema.get('enum') or []))
   if writes and enum!=writes: semantic.append(f'{eid}: state patch path enum does not equal writes allowlist')
  # update_state runtime values must be flagged runtime_injected
  for op in sc.get('patch_template') or []:
   if op.get('source_class')=='runtime_value' and not op.get('runtime_injected'): semantic.append(f'{eid}: runtime value not marked runtime_injected')
  # Declared inputs are typed: only state-class dependencies belong in canonical state.schema.
  schema_paths=set((p.get('state') or {}).get('schema_paths') or [])
  by_class=sc.get('declared_inputs_by_class') or {}
  classified=set()
  for cls, vals in by_class.items():
   if isinstance(vals,list): classified.update(vals)
  for x in by_class.get('state') or []:
   if x not in schema_paths and not any(q.startswith(x+'.') or x.startswith(q+'.') for q in schema_paths):
    semantic.append(f'{eid}: state input absent from state schema: {x}')
  # Backward-compatible safety: unclassified declared inputs remain errors.
  for x in sc.get('declared_inputs') or []:
   if x not in classified:
    semantic.append(f'{eid}: declared input absent from context contract: {x}')

 for reg in (p.get('graph') or {}).get('regions') or []:
  for eid in reg.get('element_ids') or []:
   if eid not in ids: structural.append(f"region {reg.get('id')}: missing element {eid}")
 dm=(p.get('state') or {}).get('dependency_map') or {}
 for eid,e in els.items():
  for w in (e.get('state_contract') or {}).get('writes') or []:
   if eid not in (dm.get(w) or {}).get('owners',[]): semantic.append(f'{eid}: ownership missing for {w}')
  if e.get('kind','').endswith('_gate'):
   for t in (e.get('recovery') or {}).get('derived_allowed_targets') or []:
    if t not in ids: semantic.append(f'{eid}: derived recovery target missing: {t}')
 # compiler-reported issues are semantic failures when severity=error
 compiler_issues=(p.get('validation') or {}).get('compilation_issues') or []
 for issue in compiler_issues:
  if issue.get('severity')=='error': semantic.append(f"compiler issue {issue.get('code')} at {issue.get('element_id')}: {issue.get('path') or issue.get('detail') or ''}")
 structural=list(dict.fromkeys(structural)); semantic=list(dict.fromkeys(semantic))
 diagnostics=[]
 seen_diag=set()
 for issue in compiler_issues:
  if issue.get('severity')!='error': continue
  diag=_diagnostic_from_compiler_issue(p,issue); key=(diag.get('code'),diag.get('element_id'),json.dumps(diag.get('unreachable') or []))
  if key not in seen_diag: diagnostics.append(diag); seen_diag.add(key)
 # Preserve validator-only failures that are not already represented by compiler issues.
 represented_text='\n'.join(str(x) for x in structural+semantic)
 for category,rows in [('structural',structural),('semantic',semantic)]:
  for msg in rows:
   if str(msg).startswith('compiler issue '): continue
   # Graph reachability is already richer in GRAPH_NOT_FULLY_REACHABLE.
   if 'graph not fully reachable' in str(msg).lower() and any(d.get('code')=='GRAPH_NOT_FULLY_REACHABLE' for d in diagnostics): continue
   diag=_diagnostic_from_message(p,category,msg); key=(diag.get('code'),diag.get('message'))
   if key not in seen_diag: diagnostics.append(diag); seen_diag.add(key)
 out={'status':'PASS' if not structural and not semantic else 'FAIL','structural_status':'PASS' if not structural else 'FAIL','semantic_status':'PASS' if not semantic else 'FAIL','structural_errors':structural,'semantic_errors':semantic,'diagnostics':diagnostics,'compiler_issues':compiler_issues,'source':p.get('source') or {},'entry_node':entry,'elements':len(els),'regions':len((p.get('graph') or {}).get('regions') or []),'state_paths':len(dm)}
 print(json.dumps(out,ensure_ascii=False,indent=2)); sys.exit(0 if out['status']=='PASS' else 1)
if __name__=='__main__':main()
