#!/usr/bin/env python3
from __future__ import annotations
import json,sys,re
from pathlib import Path
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
errors=[]
pol=root/'source/deterministic-first-execution-policy.json'
if not pol.exists(): errors.append({'code':'DF_POLICY_MISSING'})
else:
 p=json.loads(pol.read_text())
 if p.get('algorithmic_operation_default')!='deterministic': errors.append({'code':'DF_DEFAULT_INVALID'})
 if p.get('generated_playbooks_inherit') is not True: errors.append({'code':'DF_INHERITANCE_MISSING'})
mp=root/'verification/EXECUTION_RESPONSIBILITY_MAP.json'
if not mp.exists(): errors.append({'code':'DF_MAP_MISSING'})
else:
 d=json.loads(mp.read_text()); alg=re.compile(r'(propagation|closure|invalidation|preservation|sync|validation|materialization|hash|package|compile|binding projection)',re.I)
 for e in d.get('entries',[]):
  text=(e.get('responsibility','')+' '+e.get('element_id',''))
  if e.get('class')=='model_judgment' and alg.search(text):
   reason=(e.get('semantic_reason') or '').lower()
   if not any(t in reason for t in ['interpret','semantic','ambig','business','synthesis']):
    errors.append({'code':'DF_ALGORITHMIC_MODEL_JUDGMENT','element_id':e.get('element_id')})
  if e.get('class')=='deterministic':
   if not e.get('mechanism'): errors.append({'code':'DF_DETERMINISTIC_MECHANISM_MISSING','element_id':e.get('element_id')})
   if e.get('mechanism')=='package_local_python' and not e.get('tool_or_validator_refs'): errors.append({'code':'DF_TOOL_REF_MISSING','element_id':e.get('element_id')})
laws=(root/'PLAYBOOK_LAWS.md').read_text(encoding='utf-8')
if 'E45_DETERMINISTIC_FIRST_EXECUTION' not in laws: errors.append({'code':'DF_LAW_MISSING'})
mods=' '.join(' '.join(f.read_text(encoding='utf-8',errors='ignore').lower().split()) for f in (root/'source/modules').glob('*.yaml'))
for t in ['deterministic eligibility','algorithmic','package-local python']:
 if t not in mods: errors.append({'code':'DF_SYNTHESIS_BINDING_MISSING','token':t})
print(json.dumps({'schema_version':'1.0','validator':'VIBE_DETERMINISTIC_FIRST_EXECUTION','status':'PASS' if not errors else 'FAIL','errors':errors},ensure_ascii=False,indent=2))
sys.exit(0 if not errors else 1)
