#!/usr/bin/env python3
import json,sys
from pathlib import Path
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
errors=[]
laws=(root/'PLAYBOOK_LAWS.md').read_text(encoding='utf-8')
if 'E45_DETERMINISTIC_FIRST_EXECUTION' not in laws: errors.append('missing E44 law')
policy=root/'source/deterministic-first-execution-policy.json'
if not policy.exists(): errors.append('missing deterministic-first policy')
else:
    p=json.loads(policy.read_text())
    if p.get('algorithmic_operation_default')!='deterministic': errors.append('algorithmic default not deterministic')
    if p.get('model_fallback_requires_explicit_nondeterminism_evidence') is not True: errors.append('model fallback evidence not required')
    if p.get('generated_playbooks_inherit') is not True: errors.append('generated inheritance missing')
    if p.get('classification_before_node_synthesis') is not True: errors.append('classification not before node synthesis')
validator=root/'tools/validate_deterministic_first_execution.py'
executor=root/'tools/execute_deterministic_state_transform.py'
if not validator.exists(): errors.append('missing validator')
if not executor.exists(): errors.append('missing deterministic executor')
mp=root/'verification/EXECUTION_RESPONSIBILITY_MAP.json'
if mp.exists():
    d=json.loads(mp.read_text())
    by={e.get('element_id'):e for e in d.get('entries',[]) if isinstance(e,dict)}
    required=['N_P_ANSWER_PROPAGATION','N_K_TRACEABILITY_SYNC','N_C_DEPENDENCY_CLOSURE','N_C_INVALIDATION','N_C_PRESERVE_VALID']
    for eid in required:
        e=by.get(eid,{})
        if e.get('class')!='deterministic': errors.append(f'{eid} not deterministic')
        if 'tools/execute_deterministic_state_transform.py' not in (e.get('tool_or_validator_refs') or []): errors.append(f'{eid} missing executor ref')
mods=' '.join(' '.join(f.read_text(encoding='utf-8',errors='ignore').lower().split()) for f in (root/'source/modules').glob('*.yaml'))
for token in ['deterministic eligibility','algorithmic','package-local python']:
    if token not in mods: errors.append(f'missing synthesis token: {token}')
print(json.dumps({'status':'PASS' if not errors else 'FAIL','errors':errors},indent=2))
sys.exit(0 if not errors else 1)
