#!/usr/bin/env python3
import json, sys
from pathlib import Path
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
errors=[]
p=root/'source/constructive_correctness_policy.json'
if not p.exists(): errors.append({'code':'CC_POLICY_MISSING'})
else:
  x=json.loads(p.read_text())
  expected=['schema_constraint','typed_structure','static_template','deterministic_generator','deterministic_validator','mechanical_gate','model_instruction']
  if x.get('enforcement_precedence')!=expected: errors.append({'code':'CC_PRECEDENCE_INVALID'})
  if x.get('prompt_only_when_constructive_enforcement_available')!='forbidden': errors.append({'code':'CC_PROMPT_ONLY_NOT_FORBIDDEN'})
  if x.get('generated_playbooks_inherit') is not True: errors.append({'code':'CC_GENERATED_INHERITANCE_MISSING'})
  if x.get('model_only_exception',{}).get('requires_explicit_impossibility_evidence') is not True: errors.append({'code':'CC_MODEL_EXCEPTION_UNGROUNDED'})
laws=(root/'PLAYBOOK_LAWS.md').read_text(encoding='utf-8')
if 'E41_CONSTRUCTIVE_CORRECTNESS' not in laws: errors.append({'code':'CC_LAW_MISSING'})
mods='\n'.join(f.read_text(encoding='utf-8',errors='ignore') for f in (root/'source/modules').glob('*.yaml'))
low=mods.lower()
if not ('constructive' in low and 'correctness' in low): errors.append({'code':'CC_SYNTHESIS_BINDING_MISSING','token':'constructive correctness'})
if 'schema/type/template/generator/validator/gate' not in low: errors.append({'code':'CC_SYNTHESIS_BINDING_MISSING','token':'schema/type/template/generator/validator/gate'})
print(json.dumps({'schema_version':'1.0','validator':'VIBE_CONSTRUCTIVE_CORRECTNESS','status':'PASS' if not errors else 'FAIL','errors':errors},indent=2))
sys.exit(0 if not errors else 1)
