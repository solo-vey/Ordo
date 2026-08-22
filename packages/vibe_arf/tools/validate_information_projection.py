#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import yaml

def load(p): return yaml.safe_load(Path(p).read_text(encoding='utf-8')) or {}

def load_playbook_documents(path:Path):
    path=Path(path).resolve()
    if path.is_file():
        return [(path,load(path))]
    if path.is_dir():
        docs=[]
        for p in sorted(path.rglob('*.yaml'))+sorted(path.rglob('*.yml')):
            try: docs.append((p,load(p)))
            except Exception: continue
        return docs
    return []
def collect_ids(v,out=None):
    if out is None: out=set()
    if isinstance(v,dict):
        if isinstance(v.get('id'),str): out.add(v['id'])
        for x in v.values(): collect_ids(x,out)
    elif isinstance(v,list):
        for x in v: collect_ids(x,out)
    return out

def idx(records,key): return {str(x[key]):x for x in (records or []) if isinstance(x,dict) and x.get(key)}
def node_refs(b):
    out=[]
    for k,v in b.items():
        if k=='node_ids' or k.endswith('_node_ids'):
            if isinstance(v,list): out.extend(str(x) for x in v if x)
    return out

def validate(package:Path,playbook:Path|None=None,require_bound=False)->dict:
    package=package.resolve(); a=package/'authoring'; errors=[]; warnings=[]
    try:
        oc=load(a/'information_object_catalog.yaml'); gc=load(a/'information_group_catalog.yaml'); ac=load(a/'artifact_catalog.yaml'); fg=load(a/'information_flow_graph.yaml'); pr=load(a/'ordo_projection.yaml')
    except Exception as e: return {'schema_version':'1.0','validator':'VIBE_INFORMATION_PROJECTION','status':'FAIL','errors':[f'load: {e}'],'warnings':[]}
    objs={x['id'] for x in oc.get('objects') or [] if isinstance(x,dict) and x.get('id')}; groups={x['id'] for x in gc.get('groups') or [] if isinstance(x,dict) and x.get('id')}; arts={x['id'] for x in ac.get('artifacts') or [] if isinstance(x,dict) and x.get('id')}; gates={x['id'] for x in fg.get('nodes') or [] if isinstance(x,dict) and x.get('kind') in {'validation_gate','authority_decision'} and x.get('id')}
    specs=[('information',objs,'information_bindings','information_id'),('group',groups,'group_bindings','group_id'),('gate',gates,'gate_bindings','gate_id'),('artifact',arts,'artifact_bindings','artifact_id')]
    allrefs=set(); unbound=[]
    for label,expected,key,idkey in specs:
        bind=idx(pr.get(key),idkey)
        for x in sorted(expected-bind.keys()): errors.append(f'{label} {x}: missing projection record')
        for x in sorted(bind.keys()-expected): errors.append(f'{label} projection references unknown authoring entity {x}')
        for x,b in bind.items():
            if b.get('status')!='bound': unbound.append(f'{label}:{x}')
            allrefs.update(node_refs(b))
    if unbound:
        msg=f'{len(unbound)} authoring entities are unbound: '+', '.join(sorted(unbound))
        (errors if require_bound else warnings).append(msg)
    pbids=set()
    if playbook:
        playbook=Path(playbook).resolve()
        if not playbook.exists() or (not playbook.is_file() and not playbook.is_dir()): errors.append(f'playbook not found: {playbook}')
        else:
            docs=load_playbook_documents(playbook)
            if not docs:
                errors.append(f'no Ordo YAML documents found: {playbook}')
            pbids=set()
            for _,pb in docs: pbids.update(collect_ids(pb))
            for x in sorted(allrefs-pbids): errors.append(f'projection node {x} not found in Ordo playbook')
            managed=set((pr.get('playbook') or {}).get('managed_node_scope') or []); ignored=set((pr.get('playbook') or {}).get('ignore_node_ids') or [])
            for x in sorted(managed-ignored):
                if x not in pbids: errors.append(f'managed Ordo element {x} not found in playbook')
                elif x not in allrefs: errors.append(f'managed Ordo element {x} has no reverse authoring mapping')
            # AIM must not become a new Ordo top-level language surface.
            if (pr.get('rules') or {}).get('authoring_ids_must_not_be_ordo_extensions'):
                forbidden={'information_object_catalog','information_group_catalog','information_flow_graph','ordo_projection','authoring_model','information_groups'}
                for doc_path,pb in docs:
                    leaked=sorted(forbidden & set(pb.keys())) if isinstance(pb,dict) else []
                    for x in leaked: errors.append(f'authoring-only top-level key leaked into Ordo source {doc_path.name}: {x}')
    else: warnings.append('No playbook supplied; projection registry completeness checked without Ordo binding validation.')
    return {'schema_version':'1.0','validator':'VIBE_INFORMATION_PROJECTION','status':'PASS' if not errors else 'FAIL','require_bound':require_bound,'counts':{'information':len(objs),'groups':len(groups),'gates':len(gates),'artifacts':len(arts),'mapped_ordo_refs':len(allrefs)},'errors':errors,'warnings':warnings}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('package'); ap.add_argument('--playbook'); ap.add_argument('--require-bound',action='store_true'); a=ap.parse_args(); r=validate(Path(a.package),Path(a.playbook) if a.playbook else None,a.require_bound); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
