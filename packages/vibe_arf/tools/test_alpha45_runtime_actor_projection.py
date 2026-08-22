#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
import yaml

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(cond,msg,rows): rows.append((bool(cond),msg))
def main():
 root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve(); rows=[]
 cp=subprocess.run([sys.executable,str(root/'tools/materialize_runtime_semantic_plan.py'),str(root)],cwd=root,capture_output=True,text=True,timeout=150)
 check(cp.returncode==0,'runtime plan materialization succeeds from actor projection',rows)
 prov=json.loads((root/'runtime_projection/ACTOR_PROJECTION_PROVENANCE.json').read_text())
 check(prov.get('canonical_source_sha256')==sha(root/'source/program.ordo.yaml'),'canonical source hash preserved',rows)
 check(prov.get('derived_projection_sha256')==sha(root/'runtime_projection/program.ordo.yaml'),'projection provenance hash matches',rows)
 can=yaml.safe_load((root/'source/program.ordo.yaml').read_text()) or {}; prj=yaml.safe_load((root/'runtime_projection/program.ordo.yaml').read_text()) or {}
 can_by={x.get('id'):x for x in can.get('nodes') or [] if isinstance(x,dict)}; prj_by={x.get('id'):x for x in prj.get('nodes') or [] if isinstance(x,dict)}
 mids=[i for i,n in can_by.items() if ((n.get('node_context') or {}).get('interaction_class')=='MODEL_INTERNAL')]
 check(bool(mids),'canonical MODEL_INTERNAL nodes exist',rows)
 transformed=set(prov.get('transformed_model_internal_ids') or []); preserved=set(prov.get('preserved_package_tool_model_internal_ids') or [])
 check(set(mids)==transformed|preserved,'every MODEL_INTERNAL node is transformed or explicitly preserved as package-tool',rows)
 for i in transformed:
   c,p=can_by[i],prj_by[i]
   check(c.get('question')==p.get('model_instruction') and 'question' not in p,f'{i}: task text moved without semantic loss',rows)
   check(p.get('type')=='automatic' and p.get('action')=='AI.MODEL_STEP',f'{i}: compiler-native model-owned shape',rows)
   check(p.get('on_answer')==c.get('on_answer'),f'{i}: state update and route mechanics preserved',rows)
 plan=json.loads((root/'runtime_semantic_plan.json').read_text())
 els=plan.get('elements') or {}; mis=[]; humans=[]
 for i,e in els.items():
   traits=e.get('execution_traits') or {}; src=e.get('semantic_source') or {}; ctx=src.get('node_context') or {}
   if ctx.get('interaction_class')=='MODEL_INTERNAL' and traits.get('requires_analyst'): mis.append(i)
   if traits.get('requires_analyst'): humans.append(i)
 check(not mis,'no MODEL_INTERNAL runtime element requires analyst',rows)
 check(len(humans)==19,'runtime retains exactly 19 genuine human-owned points',rows)
 check(sum(1 for e in els.values() if (e.get('execution_traits') or {}).get('model_executed'))==146,'runtime has 146 model-executed nodes',rows)
 failed=[m for ok,m in rows if not ok]
 print(json.dumps({'status':'PASS' if not failed else 'FAIL','passed':len(rows)-len(failed),'total':len(rows),'failed':failed,'human_points':humans},ensure_ascii=False,indent=2))
 return 0 if not failed else 1
if __name__=='__main__': raise SystemExit(main())
