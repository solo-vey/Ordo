#!/usr/bin/env python3
from pathlib import Path
import json,yaml,subprocess,tempfile,sys,os
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'patterns/SIMPLE_VERIFIED_DOCUMENT_CODE_IMPLEMENTATION'
sys.path.insert(0,str(ROOT/'tools'))
from pattern_template_semantics import execution_components, canonical_outcome_edges
from pattern_data_layer_semantics import data_roles
fail=[]; passed=0
def ck(ok,msg):
 global passed
 if ok: passed+=1
 else: fail.append(msg)

def run(cmd,cwd=None):
 return subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
reg=json.loads((ROOT/'patterns/PATTERN_REGISTRY.json').read_text())
row=next((x for x in reg.get('patterns',[]) if x.get('id')=='SIMPLE_VERIFIED_DOCUMENT_CODE_IMPLEMENTATION'),{})
ck(str(row.get('version'))=='1.1','registry not v1.1')
for tag in ['safe_repository_freshness','evidence_only_target_repository','provisional_implementation_family_selection','deterministic_change_risk','persisted_result_verification']:
 ck(tag in row.get('capability_tags',[]),f'missing capability tag {tag}')
p=yaml.safe_load((BASE/'PATTERN.yaml').read_text()) or {}
ck(str((p.get('pattern') or {}).get('version'))=='1.1','PATTERN identity not v1.1')
text=(BASE/'PATTERN.yaml').read_text()
for needle in ['target_repository_role: evidence_and_mutation_target','manual_override: forbidden','fast-forward','stale evidence','verified document']:
 ck(needle.lower() in text.lower(),f'missing pattern contract: {needle}')
# v1.0 generic VIBE extensions must survive upgrade
for f in ['DOMAIN_BINDINGS.template.yaml','IMPLEMENTATION_PROFILE_CATALOG.template.yaml','IMPLEMENTATION_PROFILE.template.md','tools/select_implementation_profile.py']:
 ck((BASE/f).exists(),f'lost existing generic extension {f}')
ck((p.get('profile_selection_contract') or {}).get('selection_count')=='zero_or_one','profile selection compatibility lost')
ck((p.get('code_documentation_contract') or {}).get('repository_native_format_required') is True,'documentation obligation lost')
# Data Layer first
D=yaml.safe_load((BASE/'DATA_LAYER.template.yaml').read_text()) or {}
roles={r.get('role'):r for r in data_roles(D)}
for r in ['verified_document','target_code_source','repository_freshness_status','repository_freshness_evidence','repository_authority_boundary','implementation_family_selection_evidence','change_risk_assessment','change_risk_level','implementation_decision','verification_evidence']:
 ck(r in roles,f'missing data role {r}')
ck('execution_ids_in_canonical_data_layer: forbidden' in (BASE/'DATA_LAYER.template.yaml').read_text(),'execution IDs not forbidden in canonical data layer')
# compact execution and route safety
E=yaml.safe_load((BASE/'EXECUTION.template.yaml').read_text()) or {}
comps=execution_components(E); edges=canonical_outcome_edges(E); names=[x.get('role') for x in comps]
ck(len(comps)==8,f'expected compact 8 responsibilities, got {len(comps)}')
for r in ['refresh_local_repository','repository_freshness_gate','build_implementation_plan_and_classify_scope','local_scope_gate','execute_implementation_and_verify','implementation_verified_gate']:
 ck(r in names,f'missing execution role {r}')
ck(any(e.get('from_role')=='repository_freshness_gate' and e.get('outcome')=='BLOCKED' and e.get('terminal')=='REPOSITORY_REFRESH_BLOCKED' for e in edges),'refresh BLOCKED terminal missing')
ck(any(e.get('from_role')=='local_scope_gate' and e.get('outcome')=='HANDOFF_REQUIRED' and e.get('terminal')=='HANDOFF_REQUIRED' for e in edges),'HANDOFF terminal missing')
# mutation has no route before both gates: sole inbound to mutation is local_scope_gate LOCAL_SAFE
inbound=[e for e in edges if e.get('to_role')=='execute_implementation_and_verify']
ck(len(inbound)==1 and inbound[0].get('from_role')=='local_scope_gate' and inbound[0].get('outcome')=='LOCAL_SAFE','mutation path bypasses risk gate')
# risk helper: LOW -> local, HIGH -> handoff, invalid -> fail closed
risk=BASE/'tools/assess_implementation_change_risk.py'
dims=['scope_locality','ownership_clarity','shared_contract_impact','blast_radius','cross_module_dependency','backward_compatibility','migration_operational_impact','verification_confidence']
with tempfile.TemporaryDirectory() as td:
 td=Path(td)
 for name,data,code,decision in [
  ('low',{d:'LOW' for d in dims},0,'LOCAL_SAFE'),
  ('high',{**{d:'LOW' for d in dims},'blast_radius':'HIGH'},0,'HANDOFF_REQUIRED'),
  ('invalid',{d:'LOW' for d in dims if d!='verification_confidence'},2,None),
 ]:
  f=td/(name+'.json'); f.write_text(json.dumps(data))
  cp=run([sys.executable,str(risk),'--assessment-json',str(f)])
  ck(cp.returncode==code,f'risk {name} rc {cp.returncode} != {code}')
  try: out=json.loads(cp.stdout)
  except: out={}
  if decision: ck(out.get('implementation_decision')==decision,f'risk {name} decision mismatch')
  else: ck(out.get('status')=='INVALID','invalid risk did not fail closed')
# git helper: non-git NOT_APPLICABLE, dirty and no-upstream BLOCKED; behind-only ff succeeds
fresh=BASE/'tools/refresh_local_git_repository.py'
with tempfile.TemporaryDirectory() as td:
 td=Path(td)
 nongit=td/'nongit'; nongit.mkdir()
 cp=run([sys.executable,str(fresh),'--repo',str(nongit)]); out=json.loads(cp.stdout); ck(out.get('status')=='NOT_APPLICABLE','non-git not NOT_APPLICABLE')
 # no-upstream
 repo=td/'repo'; repo.mkdir(); run(['git','init','-q'],repo); run(['git','config','user.email','a@b.c'],repo); run(['git','config','user.name','t'],repo); (repo/'a').write_text('1'); run(['git','add','a'],repo); run(['git','commit','-qm','i'],repo)
 cp=run([sys.executable,str(fresh),'--repo',str(repo)]); out=json.loads(cp.stdout); ck(out.get('status')=='BLOCKED' and out.get('reason')=='upstream_missing','no-upstream did not block')
 (repo/'a').write_text('dirty'); cp=run([sys.executable,str(fresh),'--repo',str(repo)]); out=json.loads(cp.stdout); ck(out.get('status')=='BLOCKED' and out.get('reason')=='dirty_worktree','dirty repo did not block')
 # behind-only setup
 bare=td/'remote.git'; run(['git','init','--bare','-q',str(bare)])
 seed=td/'seed'; run(['git','clone','-q',str(bare),str(seed)]); run(['git','config','user.email','a@b.c'],seed); run(['git','config','user.name','t'],seed); (seed/'x').write_text('1'); run(['git','add','x'],seed); run(['git','commit','-qm','one'],seed); run(['git','push','-qu','origin','HEAD'],seed)
 local=td/'local'; run(['git','clone','-q',str(bare),str(local)])
 (seed/'x').write_text('2'); run(['git','commit','-qam','two'],seed); run(['git','push','-q'],seed)
 cp=run([sys.executable,str(fresh),'--repo',str(local)]); out=json.loads(cp.stdout); ck(cp.returncode==0 and out.get('status')=='UPDATED','behind-only did not fast-forward safely')
 ck((local/'x').read_text()=='2','fast-forward did not update persisted file')
print(json.dumps({'status':'PASS' if not fail else 'FAIL','passed':passed,'failed':len(fail),'failures':fail},indent=2))
raise SystemExit(1 if fail else 0)
