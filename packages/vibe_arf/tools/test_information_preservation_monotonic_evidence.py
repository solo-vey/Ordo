#!/usr/bin/env python3
import json,sys,yaml,tempfile,subprocess
from pathlib import Path
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
errors=[]
laws=(root/'PLAYBOOK_LAWS.md').read_text(encoding='utf-8')
if 'E46_INFORMATION_PRESERVATION_MONOTONIC_EVIDENCE' not in laws: errors.append('missing E46 law')
policy=root/'source/information-preservation-policy.json'
if not policy.exists(): errors.append('missing policy')
else:
 p=json.loads(policy.read_text())
 for k,v in {
  'authoritative_known_cannot_silently_downgrade':True,
  'whole_object_replace_for_authoritative_evidence_forbidden':True,
  'field_level_provenance_required':True,
  'generated_playbooks_inherit':True}.items():
  if p.get(k)!=v: errors.append(f'policy {k} != {v}')
 if p.get('default_update_semantics') not in ('merge_append','field_merge_append'): errors.append('default update semantics not merge/append')
tool=root/'tools/merge_authoritative_evidence.py'
validator=root/'tools/validate_information_preservation.py'
if not tool.exists(): errors.append('missing merge tool')
if not validator.exists(): errors.append('missing validator')
mods='\n'.join(f.read_text(encoding='utf-8',errors='ignore') for f in (root/'source/modules').glob('*.yaml')).lower()
for tok in ['field-level provenance','monotonic evidence','merge/append','known → unknown']:
 if tok not in mods: errors.append(f'missing module token {tok}')
cat=yaml.safe_load((root/'authoring/information_object_catalog.yaml').read_text())
if not any(o.get('id')=='I_INFORMATION_PRESERVATION_CONTRACT' for o in cat.get('objects',[])): errors.append('missing AIM preservation contract')
# behavioral smoke: known field survives merge and downgrade is rejected
if tool.exists():
 with tempfile.TemporaryDirectory() as td:
  td=Path(td); base=td/'base.json'; patch=td/'patch.json'; out=td/'out.json'
  base.write_text(json.dumps({'endpoint':{'state':'known','value':'/v1/x','provenance':{'source':'user','ref':'u1'}}}))
  patch.write_text(json.dumps({'timeout':{'state':'known','value':30,'provenance':{'source':'doc','ref':'d1'}}}))
  r=subprocess.run([sys.executable,str(tool),'--base',str(base),'--patch',str(patch),'--out',str(out)],capture_output=True,text=True)
  if r.returncode!=0: errors.append('merge smoke failed')
  else:
   d=json.loads(out.read_text())
   if d.get('endpoint',{}).get('value')!='/v1/x' or d.get('timeout',{}).get('value')!=30: errors.append('merge did not preserve/append')
  patch.write_text(json.dumps({'endpoint':{'state':'unknown','value':None,'provenance':{'source':'model','ref':'m1'}}}))
  r=subprocess.run([sys.executable,str(tool),'--base',str(base),'--patch',str(patch),'--out',str(out)],capture_output=True,text=True)
  if r.returncode==0: errors.append('known->unknown downgrade not rejected')
print(json.dumps({'status':'PASS' if not errors else 'FAIL','errors':errors},indent=2,ensure_ascii=False))
sys.exit(0 if not errors else 1)
