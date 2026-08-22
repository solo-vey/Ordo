#!/usr/bin/env python3
import json,sys,yaml
from pathlib import Path
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
errors=[]
p=root/'source/information-preservation-policy.json'
if not p.exists(): errors.append('missing policy')
else:
 d=json.loads(p.read_text())
 for k in ['authoritative_known_cannot_silently_downgrade','whole_object_replace_for_authoritative_evidence_forbidden','field_level_provenance_required','generated_playbooks_inherit']:
  if d.get(k) is not True: errors.append(k)
mods='\n'.join(f.read_text(encoding='utf-8',errors='ignore').lower() for f in (root/'source/modules').glob('*.yaml'))
for t in ['field-level provenance','monotonic evidence','merge/append','known → unknown']:
 if t not in mods: errors.append('missing '+t)
cat=yaml.safe_load((root/'authoring/information_object_catalog.yaml').read_text())
if not any(o.get('id')=='I_INFORMATION_PRESERVATION_CONTRACT' for o in cat.get('objects',[])): errors.append('missing AIM object')
print(json.dumps({'status':'PASS' if not errors else 'FAIL','errors':errors},indent=2)); sys.exit(0 if not errors else 1)
