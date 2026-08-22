#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

def ids_from_graph(d):
    return {x.get('id') for k in ('nodes','gates') for x in (d.get(k) or []) if isinstance(x,dict) and x.get('id')}
def refs(case):
    out=set()
    def walk(v,k=''):
        if isinstance(v,dict):
            for kk,vv in v.items():
                if kk in {'node','current_node','id'} and isinstance(vv,str) and (vv.startswith('N_') or vv.startswith('G_')): out.add(vv)
                walk(vv,kk)
        elif isinstance(v,list):
            for x in v: walk(x,k)
    walk(case); return out
def project(graph_path,test_path,out_path):
    g=yaml.safe_load(Path(graph_path).read_text()) or {}; t=yaml.safe_load(Path(test_path).read_text()) or {}
    valid=ids_from_graph(g); kept=[]; removed=[]
    for c in t.get('test_cases',[]) or []:
        rr=refs(c); (kept if rr<=valid else removed).append(c)
    out={'test_cases':kept}
    Path(out_path).write_text(yaml.safe_dump(out,sort_keys=False),encoding='utf-8')
    return {'status':'PASS','kept':len(kept),'removed':len(removed),'removed_ids':[x.get('id') for x in removed],'rule':'every retained test reference resolves in retained graph'}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('graph'); ap.add_argument('tests'); ap.add_argument('output'); a=ap.parse_args()
    r=project(a.graph,a.tests,a.output); print(json.dumps(r,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
