#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path
import yaml

def yl(p):
    try: d=yaml.safe_load(p.read_text(encoding='utf-8'))
    except Exception as e: raise ValueError(f'{p}: {e}')
    if not isinstance(d,dict): raise ValueError(f'{p}: expected mapping')
    return d

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); args=ap.parse_args()
    r=Path(args.root).resolve(); d=r/'design'; a=r/'authoring'; findings=[]
    required=['MODEL_BUNDLE.yaml','information_dependency_graph.yaml','variable_catalog.yaml','variable_group_catalog.yaml','artifact_catalog.yaml','playbook_projection.yaml','DATA_FLOW_PACKAGE.zip']
    for n in required:
        if not (d/n).is_file(): findings.append({'code':'MISSING_PUBLICATION_RESOURCE','path':f'design/{n}'})
    if findings:
        print(json.dumps({'status':'failed','findings':findings},indent=2)); return 1
    bundle=yl(d/'MODEL_BUNDLE.yaml'); c=bundle.get('canonical_sources') or {}
    expected_refs={'graph':'information_dependency_graph.yaml','variable_catalog':'variable_catalog.yaml','variable_group_catalog':'variable_group_catalog.yaml','artifact_catalog':'artifact_catalog.yaml','playbook_projection':'playbook_projection.yaml'}
    for k,v in expected_refs.items():
        if c.get(k)!=v: findings.append({'code':'BAD_CANONICAL_SOURCE_REF','key':k,'expected':v,'actual':c.get(k)})
    if bundle.get('generated_from')!='authoring/': findings.append({'code':'BAD_CANONICAL_UPSTREAM'})
    if bundle.get('publication_semantics')!='authoring_adapter_only': findings.append({'code':'SEMANTIC_AUTHORITY_LEAK'})
    obj=yl(a/'information_object_catalog.yaml'); var=yl(d/'variable_catalog.yaml')
    aids={str(x['id']) for x in obj.get('objects',[]) if isinstance(x,dict) and x.get('id')}; pids={str(x['id']) for x in var.get('variables',[]) if isinstance(x,dict) and x.get('id')}
    if aids!=pids: findings.append({'code':'OBJECT_ID_DIVERGENCE','missing':sorted(aids-pids),'extra':sorted(pids-aids)})
    grp=yl(a/'information_group_catalog.yaml'); pgrp=yl(d/'variable_group_catalog.yaml')
    am={str(x['id']):list(x.get('members') or []) for x in grp.get('groups',[]) if isinstance(x,dict) and x.get('id')}; pm={str(x['id']):list(x.get('member_variables') or []) for x in pgrp.get('groups',[]) if isinstance(x,dict) and x.get('id')}
    if am!=pm: findings.append({'code':'GROUP_DIVERGENCE'})
    gf=yl(a/'information_flow_graph.yaml'); pg=yl(d/'information_dependency_graph.yaml')
    an={str(x['id']) for x in gf.get('nodes',[]) if isinstance(x,dict) and x.get('id')}; pn={str(x['id']) for x in pg.get('nodes',[]) if isinstance(x,dict) and x.get('id')}
    if an!=pn: findings.append({'code':'GRAPH_NODE_DIVERGENCE','missing':sorted(an-pn),'extra':sorted(pn-an)})
    ae={(str(x.get('from')),str(x.get('to')),str(x.get('type'))) for x in gf.get('edges',[]) if isinstance(x,dict)}; pe={(str(x.get('from')),str(x.get('to')),str(x.get('type'))) for x in pg.get('edges',[]) if isinstance(x,dict)}
    if ae!=pe: findings.append({'code':'GRAPH_EDGE_DIVERGENCE','missing_count':len(ae-pe),'extra_count':len(pe-ae)})
    ac=yl(a/'artifact_catalog.yaml'); pac=yl(d/'artifact_catalog.yaml')
    ai={str(x['id']) for x in ac.get('artifacts',[]) if isinstance(x,dict) and x.get('id')}; pi={str(x['id']) for x in pac.get('artifacts',[]) if isinstance(x,dict) and x.get('id')}
    if ai!=pi: findings.append({'code':'ARTIFACT_DIVERGENCE'})
    op=yl(a/'ordo_projection.yaml'); pop=yl(d/'playbook_projection.yaml')
    if pop.get('source_projection_sha256')!=sha(a/'ordo_projection.yaml') or pop.get('information_bindings')!=op.get('information_bindings') or pop.get('group_bindings')!=op.get('group_bindings'):
        findings.append({'code':'PLAYBOOK_PROJECTION_DIVERGENCE'})
    upstream_expected={n:sha(a/n) for n in ['information_object_catalog.yaml','information_group_catalog.yaml','information_flow_graph.yaml','artifact_catalog.yaml','ordo_projection.yaml']}
    if bundle.get('upstream_sha256')!=upstream_expected: findings.append({'code':'STALE_PUBLICATION_HASHES'})
    with zipfile.ZipFile(d/'DATA_FLOW_PACKAGE.zip') as z: names={n for n in z.namelist() if not n.endswith('/')}
    required_archive=set(['MODEL_BUNDLE.yaml','information_dependency_graph.yaml','variable_catalog.yaml','variable_group_catalog.yaml','artifact_catalog.yaml','playbook_projection.yaml'])
    if not required_archive<=names: findings.append({'code':'DATA_FLOW_ARCHIVE_INCOMPLETE','missing':sorted(required_archive-names)})
    # Editor adapter discovery contract: any YAML manifest with canonical_sources.graph, graph nodes+edges, refs resolvable.
    if not isinstance(pg.get('nodes'),list) or not isinstance(pg.get('edges'),list): findings.append({'code':'EDITOR_DISCOVERY_GRAPH_SHAPE_INVALID'})
    result={'status':'passed' if not findings else 'failed','publication_semantics':'authoring_adapter_only','authoring_object_count':len(aids),'graph_nodes':len(an),'graph_edges':len(ae),'artifact_count':len(ai),'findings':findings}
    print(json.dumps(result,indent=2,sort_keys=True)); return 0 if not findings else 1
if __name__=='__main__': raise SystemExit(main())
