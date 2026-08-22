#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import yaml

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--output'); ns=ap.parse_args(); root=Path(ns.root).resolve()
 objs=yaml.safe_load((root/'authoring/information_object_catalog.yaml').read_text()) or {}; graph=yaml.safe_load((root/'authoring/information_flow_graph.yaml').read_text()) or {}
 om={o['id']:o for o in objs.get('objects',[])}; nm={n['id']:n for n in graph.get('nodes',[])}; edges=graph.get('edges',[])
 opp=[]
 # Single Responsibility: one gate should own one cohesive semantic group unless explicitly marked cross-group.
 for n in graph.get('nodes',[]):
  if n.get('kind')!='validation_gate' or n.get('cross_group_validation') is True: continue
  covers=n.get('covers',[]) or []; groups=sorted({om[x].get('group_id') for x in covers if x in om and om[x].get('group_id')})
  if len(groups)>1: opp.append({'rule_id':'SINGLE_RESPONSIBILITY','entity_id':n['id'],'groups':groups,'score_effect':0})
 # RUN->GATE semantic pairing: every covered object has direct validated_by edge to that gate.
 vedges={(e.get('from'),e.get('to')) for e in edges if e.get('type')=='validated_by'}
 for n in graph.get('nodes',[]):
  if n.get('kind')!='validation_gate' or n.get('local_validation') is not True: continue
  for iid in n.get('covers',[]) or []:
   if (iid,n['id']) not in vedges: opp.append({'rule_id':'RUN_TO_GATE','entity_id':iid,'gate_id':n['id'],'reason':'covered_without_validated_by_edge','score_effect':0})
 # Deterministic-first conservative detector: only explicit deterministic-required contracts are eligible for this hard diagnostic.
 for iid,o in om.items():
  origins=set(o.get('origins',[]) or [])
  if o.get('deterministic_required') is True and 'model_derivation' in origins:
   opp.append({'rule_id':'DETERMINISTIC_FIRST_EXECUTION','entity_id':iid,'reason':'model_origin_for_deterministic_required_information','score_effect':0})
 counts={r:sum(1 for x in opp if x['rule_id']==r) for r in ['SINGLE_RESPONSIBILITY','RUN_TO_GATE','DETERMINISTIC_FIRST_EXECUTION']}
 out={'format':'vibe-data-layer-architecture-analysis/v1','semantic_source':'canonical_data_layer','mode':'OPPORTUNITY_DIAGNOSTIC','score_effect':0,'summary':counts,'opportunities':opp}
 s=json.dumps(out,indent=2,sort_keys=True)+'\n';
 if ns.output: Path(ns.output).write_text(s)
 else: print(s,end='')
 return 0
if __name__=='__main__': raise SystemExit(main())
