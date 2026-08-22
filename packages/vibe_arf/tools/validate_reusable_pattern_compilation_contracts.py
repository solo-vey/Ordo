#!/usr/bin/env python3
from pathlib import Path
import json, yaml, sys
from pattern_template_semantics import execution_components, canonical_outcome_edges
ROOT=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
reg=json.loads((ROOT/'patterns/PATTERN_REGISTRY.json').read_text())
fail=[]; checked=0
advanced={'DOCUMENT_RECONCILIATION_VERIFICATION','VERIFIED_DOCUMENT_JIRA_TASK_MATERIALIZATION','VERIFIED_DOCUMENT_CODE_IMPLEMENTATION','EXECUTION_DEBUG_EVIDENCE_EXPORT'}
for r in reg.get('patterns',[]):
    pid=r['id']; base=ROOT/'patterns'/r['path']
    for fn in ('PATTERN.yaml','DATA_LAYER.template.yaml','EXECUTION.template.yaml'):
        if not (base/fn).exists(): fail.append(f'{pid}: missing {fn}')
    if pid not in advanced: continue
    checked+=1
    if not (base/'COMPILATION_CONTRACT.md').exists(): fail.append(f'{pid}: missing COMPILATION_CONTRACT.md')
    pdef=yaml.safe_load((base/'PATTERN.yaml').read_text()) or {}
    ex=yaml.safe_load((base/'EXECUTION.template.yaml').read_text()) or {}
    comps=execution_components(ex); roles=[x.get('role') for x in comps]
    edges=canonical_outcome_edges(ex)
    if not comps: fail.append(f'{pid}: no execution responsibilities')
    if len(roles)!=len(set(roles)): fail.append(f'{pid}: duplicate execution roles')
    rs=set(roles)
    if not edges: fail.append(f'{pid}: no canonical outcome edges')
    for e in edges:
        if e.get('from_role') not in rs: fail.append(f'{pid}: unresolved canonical outcome source {e}')
        target=e.get('to_role'); terminal=e.get('terminal')
        if target not in rs and not terminal and not (isinstance(target,str) and target and target.upper()==target): fail.append(f'{pid}: unresolved canonical outcome destination {e}')
        if not e.get('outcome'): fail.append(f'{pid}: missing exact outcome token {e}')
    pc=(pdef.get('execution_compilation_contract') or {})
    text=json.dumps(pc,sort_keys=True).lower()+" "+(base/'COMPILATION_CONTRACT.md').read_text().lower()
    for needle in ('on_answer.next','on_pass','on_fail','fail closed','reachable'):
        if needle not in text: fail.append(f'{pid}: compiler contract missing {needle}')
    if not ((ex.get('projection_semantics') or {}).get('compiler_valid_lowering_required')):
        fail.append(f'{pid}: execution template does not require compiler-valid lowering')
print(json.dumps({'status':'PASS' if not fail else 'FAIL','advanced_patterns_checked':checked,'registered_patterns':len(reg.get('patterns',[])),'failures':fail},indent=2))
raise SystemExit(1 if fail else 0)
