#!/usr/bin/env python3
from pathlib import Path
import json, yaml, subprocess, sys, tempfile, shutil
ROOT=Path(__file__).resolve().parents[1]
fail=[]; passed=0
def ck(ok,msg):
 global passed
 if ok: passed+=1
 else: fail.append(msg)
reg=json.loads((ROOT/'patterns/PATTERN_REGISTRY.json').read_text())
ids={p['id']:str(p['version']) for p in reg.get('patterns',[])}
expected={'DOCUMENT_RECONCILIATION_VERIFICATION':'1.2','VERIFIED_DOCUMENT_JIRA_TASK_MATERIALIZATION':'1.1','VERIFIED_DOCUMENT_CODE_IMPLEMENTATION':'1.2','EXECUTION_DEBUG_EVIDENCE_EXPORT':'1.1'}
for pid,ver in expected.items():
 ck(ids.get(pid)==ver,f'{pid}: registry version mismatch')
 base=ROOT/'patterns'/pid
 for fn in ('PATTERN.yaml','DATA_LAYER.template.yaml','EXECUTION.template.yaml','COMPILATION_CONTRACT.md'):
  ck((base/fn).exists(),f'{pid}: missing {fn}')
 ex=yaml.safe_load((base/'EXECUTION.template.yaml').read_text()) or {}
 comps=ex.get('components',ex.get('required_responsibilities',[])) or []
 edges=ex.get('outcome_edges',ex.get('edges',[])) or []
 ck(bool(comps),f'{pid}: responsibilities empty')
 ck(bool(edges),f'{pid}: canonical outcomes empty')
 ck(all(e.get('outcome') for e in edges),f'{pid}: canonical outcome token missing')
# exact special semantics
code=yaml.safe_load((ROOT/'patterns/VERIFIED_DOCUMENT_CODE_IMPLEMENTATION/EXECUTION.template.yaml').read_text())
outcomes={e.get('outcome') for e in code.get('outcome_edges',[]) if e.get('from_role')=='implementation_branch_gate'}
ck(outcomes=={'NO_LOCAL_CHANGE','HANDOFF_REQUIRED','LOCAL_SAFE'},f'code implementation decision outcomes changed: {outcomes}')
dbg=yaml.safe_load((ROOT/'patterns/EXECUTION_DEBUG_EVIDENCE_EXPORT/EXECUTION.template.yaml').read_text())
ck(any(e.get('outcome')=='DEBUG_NOT_REQUIRED' for e in dbg.get('outcome_edges',[])),'debug NOT_REQUIRED path missing')
jira=yaml.safe_load((ROOT/'patterns/VERIFIED_DOCUMENT_JIRA_TASK_MATERIALIZATION/DATA_LAYER.template.yaml').read_text())
ck('testing_identifiers_are_never_invented' in jira.get('constraints',[]),'Jira testing identifier anti-invention invariant missing')
rec=yaml.safe_load((ROOT/'patterns/DOCUMENT_RECONCILIATION_VERIFICATION/DATA_LAYER.template.yaml').read_text())
ck('document_mutation_invalidates_all_acceptance_evidence_bound_to_prior_document_identity' in rec.get('constraints',[]),'document mutation stale-evidence invariant missing')
# compiler contract validator must pass
p=subprocess.run([sys.executable,str(ROOT/'tools/validate_reusable_pattern_compilation_contracts.py'),str(ROOT)],capture_output=True,text=True)
ck(p.returncode==0,'reusable pattern compilation contract validator failed: '+p.stdout[-1000:])

# Advanced patterns must not auto-match generic artifacts by kind alone.
disc=subprocess.run([sys.executable,str(ROOT/'tools/discover_data_layer_patterns.py'),str(ROOT)],capture_output=True,text=True)
try: suggestions=json.loads(disc.stdout).get('suggestions',[])
except Exception: suggestions=[]
advanced_ids=set(expected)
ck(not any(x.get('pattern_id') in advanced_ids for x in suggestions),'advanced patterns falsely auto-selected without semantic capability requirement')

policy=json.loads((ROOT/'source/reusable-pattern-compiler-lowering-policy.json').read_text())
ck(policy.get('domain_boundary',{}).get('generic_pattern_core_forbids') is not None,'generic/domain boundary missing')
print(json.dumps({'status':'PASS' if not fail else 'FAIL','passed':passed,'failed':len(fail),'failures':fail},indent=2))
raise SystemExit(1 if fail else 0)
