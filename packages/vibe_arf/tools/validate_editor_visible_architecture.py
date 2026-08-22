#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, yaml

def y(p): return yaml.safe_load(p.read_text(encoding='utf-8'))
def validate(root: Path) -> dict:
    errors=[]
    try: surf=json.loads((root/'editor/architecture_surface.json').read_text(encoding='utf-8'))
    except Exception as e: return {'status':'FAIL','surface_reconstructible':False,'errors':[f'SURFACE_UNREADABLE:{e}']}
    groups=(y(root/'authoring/information_group_catalog.yaml') or {}).get('groups',[])
    objs=(y(root/'authoring/information_object_catalog.yaml') or {}).get('objects',[])
    flow=y(root/'authoring/information_flow_graph.yaml') or {}
    proj=(y(root/'authoring/ordo_projection.yaml') or {}).get('information_bindings',[])
    arts=(y(root/'authoring/artifact_catalog.yaml') or {}).get('artifacts',[])
    sg={x.get('id') for x in surf.get('groups',[])}; so={x.get('id') for x in surf.get('variables',[])}
    sb={x.get('information_id') for x in surf.get('bindings',[])}
    if {x.get('id') for x in groups}-sg: errors.append('GROUPS_NOT_RECONSTRUCTIBLE')
    if {x.get('id') for x in objs}-so: errors.append('VARIABLES_NOT_RECONSTRUCTIBLE')
    canonical_edges={(e.get('from'),e.get('to'),e.get('type')) for e in flow.get('edges',[]) if isinstance(e,dict)}
    surface_edges={(e.get('from'),e.get('to'),e.get('type')) for e in surf.get('dataflow_edges',[]) if isinstance(e,dict)}
    if canonical_edges-surface_edges: errors.append('DATAFLOW_EDGES_NOT_RECONSTRUCTIBLE')
    if {x.get('information_id') for x in proj}-sb: errors.append('BINDINGS_NOT_RECONSTRUCTIBLE')
    req_mat={a.get('id') for a in arts if (a.get('materialization') or {}).get('required')}
    got_mat={a.get('artifact_id') for a in surf.get('materialization',[])}
    if req_mat-got_mat: errors.append('MATERIALIZATION_NOT_RECONSTRUCTIBLE')
    archives=[a for a in arts if a.get('kind')=='archive']
    ap=surf.get('archive_path') or {}
    if archives and (ap.get('artifact_id')!=archives[0].get('id') or not ap.get('path_chain')): errors.append('ARCHIVE_PATH_NOT_RECONSTRUCTIBLE')
    policy=json.loads((root/'source/editor-visible-architecture-policy.json').read_text(encoding='utf-8'))
    for key in policy.get('required_surfaces',[]):
        if not surf.get(key): errors.append('EMPTY_REQUIRED_SURFACE:'+key)
    return {'status':'PASS' if not errors else 'FAIL','surface_reconstructible':not errors,'errors':errors,
      'counts':{'groups':len(surf.get('groups',[])),'variables':len(surf.get('variables',[])),'dataflow_edges':len(surf.get('dataflow_edges',[])),'bindings':len(surf.get('bindings',[])),'materialization':len(surf.get('materialization',[]))}}
if __name__=='__main__':
    r=validate(Path(__file__).resolve().parents[1]); print(json.dumps(r,indent=2)); raise SystemExit(0 if r['status']=='PASS' else 1)
