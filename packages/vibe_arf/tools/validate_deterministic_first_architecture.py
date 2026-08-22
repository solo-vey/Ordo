#!/usr/bin/env python3
from __future__ import annotations
import json, sys, yaml
from pathlib import Path
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
errors=[]
def loadj(rel):
 p=root/rel
 if not p.is_file(): errors.append({'code':'MISSING_FILE','path':rel}); return {}
 try:return json.loads(p.read_text(encoding='utf-8'))
 except Exception as e: errors.append({'code':'INVALID_JSON','path':rel,'error':str(e)}); return {}
pol=loadj('source/deterministic-first-architecture-policy.json')
patch=loadj('source/state-patch-v1-contract.json')
safe=loadj('source/generated-playbook-safe-node-profiles.json')
if pol.get('policy_id')!='DETERMINISTIC_FIRST_ARCHITECTURE': errors.append({'code':'POLICY_ID'})
for k,v in pol.get('responsibility_ownership',{}).items():
 if v!='deterministic': errors.append({'code':'MECHANICAL_OWNER_NOT_DETERMINISTIC','class':k})
sp=pol.get('state_patch',{})
for k in ['allowed_roots_required','base_state_hash_required','fail_closed_on_stale_baseline']:
 if sp.get(k) is not True: errors.append({'code':'STATE_PATCH_GUARD_MISSING','guard':k})
if patch.get('contract_id')!='state_patch_v1': errors.append({'code':'STATE_PATCH_CONTRACT'})
profiles=safe.get('profiles',{})
if 'state_patch_v1' not in ' '.join(profiles.get('MODEL_AUTOMATIC',{}).get('conditional_requirements',[])): errors.append({'code':'MODEL_PATCH_INHERITANCE'})
if 'state_updates_v1' not in ' '.join(profiles.get('DETERMINISTIC_RUN',{}).get('required',[])): errors.append({'code':'DETERMINISTIC_ENVELOPE_INHERITANCE'})
for rel in ['tools/apply_state_patch_v1.py','tools/hydrate_deterministic_evidence.py','authoring_templates/reusable/DETERMINISTIC_FIRST_ARCHITECTURE.template.yaml']:
 if not (root/rel).is_file(): errors.append({'code':'REQUIRED_ASSET_MISSING','path':rel})
print(json.dumps({'schema_version':'1.0','validator':'DETERMINISTIC_FIRST_ARCHITECTURE','status':'PASS' if not errors else 'FAIL','errors':errors},ensure_ascii=False,indent=2))
raise SystemExit(0 if not errors else 1)
