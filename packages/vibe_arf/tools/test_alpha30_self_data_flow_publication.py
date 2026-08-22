#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys, zipfile
from pathlib import Path
import yaml


def load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding='utf-8'))

def sha(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def check(cond, msg):
    if not cond:
        raise AssertionError(msg)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    args=ap.parse_args()
    root=Path(args.root).resolve()
    results=[]
    def case(name, fn):
        try:
            fn(); results.append((name, True, ''))
        except Exception as e:
            results.append((name, False, str(e)))

    design=root/'design'
    authoring=root/'authoring'

    case('R45_MODEL_BUNDLE_PRESENT', lambda: check((design/'MODEL_BUNDLE.yaml').is_file(), 'design/MODEL_BUNDLE.yaml missing'))
    case('R46_PUBLISHED_GRAPH_PRESENT', lambda: check((design/'information_dependency_graph.yaml').is_file(), 'published graph missing'))
    case('R47_PUBLISHED_VARIABLE_CATALOG_PRESENT', lambda: check((design/'variable_catalog.yaml').is_file(), 'variable catalog missing'))
    case('R48_PUBLISHED_GROUP_CATALOG_PRESENT', lambda: check((design/'variable_group_catalog.yaml').is_file(), 'group catalog missing'))
    case('R49_PUBLISHED_ARTIFACT_CATALOG_PRESENT', lambda: check((design/'artifact_catalog.yaml').is_file(), 'artifact catalog missing'))
    case('R50_PUBLISHED_PLAYBOOK_PROJECTION_PRESENT', lambda: check((design/'playbook_projection.yaml').is_file(), 'playbook projection missing'))
    case('R51_DATA_FLOW_PACKAGE_PRESENT', lambda: check((design/'DATA_FLOW_PACKAGE.zip').is_file(), 'DATA_FLOW_PACKAGE.zip missing'))

    def bundle_contract():
        b=load_yaml(design/'MODEL_BUNDLE.yaml')
        c=b.get('canonical_sources') or {}
        check(c.get('graph')=='information_dependency_graph.yaml','graph canonical source mismatch')
        for key,name in [('variable_catalog','variable_catalog.yaml'),('variable_group_catalog','variable_group_catalog.yaml'),('artifact_catalog','artifact_catalog.yaml'),('playbook_projection','playbook_projection.yaml')]:
            check(c.get(key)==name, f'{key} canonical source mismatch')
        check(b.get('generated_from')=='authoring/', 'bundle must declare authoring/ as canonical upstream')
        check(b.get('publication_semantics')=='authoring_adapter_only', 'publication must remain authoring adapter, not Ordo semantics')
    case('R52_MODEL_BUNDLE_CONTRACT', bundle_contract)

    def object_equivalence():
        a=load_yaml(authoring/'information_object_catalog.yaml')
        p=load_yaml(design/'variable_catalog.yaml')
        aids={str(x['id']) for x in a.get('objects',[]) if isinstance(x,dict) and x.get('id')}
        pids={str(x['id']) for x in p.get('variables',[]) if isinstance(x,dict) and x.get('id')}
        check(aids==pids, f'published information ids differ: missing={sorted(aids-pids)[:5]} extra={sorted(pids-aids)[:5]}')
    case('R53_INFORMATION_OBJECT_EQUIVALENCE', object_equivalence)

    def group_equivalence():
        a=load_yaml(authoring/'information_group_catalog.yaml')
        p=load_yaml(design/'variable_group_catalog.yaml')
        am={str(x['id']):set(map(str,x.get('members',[]))) for x in a.get('groups',[]) if isinstance(x,dict) and x.get('id')}
        pm={str(x['id']):set(map(str,x.get('member_variables',[]))) for x in p.get('groups',[]) if isinstance(x,dict) and x.get('id')}
        check(am==pm, 'published semantic groups/members differ from AIM')
    case('R54_INFORMATION_GROUP_EQUIVALENCE', group_equivalence)

    def graph_equivalence():
        a=load_yaml(authoring/'information_flow_graph.yaml')
        p=load_yaml(design/'information_dependency_graph.yaml')
        an={str(x['id']) for x in a.get('nodes',[]) if isinstance(x,dict) and x.get('id')}
        pn={str(x['id']) for x in p.get('nodes',[]) if isinstance(x,dict) and x.get('id')}
        check(an==pn, f'published graph node ids differ missing={sorted(an-pn)[:5]} extra={sorted(pn-an)[:5]}')
        ae={(str(e.get('from')),str(e.get('to')),str(e.get('type'))) for e in a.get('edges',[]) if isinstance(e,dict)}
        pe={(str(e.get('from')),str(e.get('to')),str(e.get('type'))) for e in p.get('edges',[]) if isinstance(e,dict)}
        check(ae==pe, f'published graph edges differ missing={len(ae-pe)} extra={len(pe-ae)}')
    case('R55_INFORMATION_GRAPH_EQUIVALENCE', graph_equivalence)

    def artifact_equivalence():
        a=load_yaml(authoring/'artifact_catalog.yaml')
        p=load_yaml(design/'artifact_catalog.yaml')
        aids={str(x['id']) for x in a.get('artifacts',[]) if isinstance(x,dict) and x.get('id')}
        pids={str(x['id']) for x in p.get('artifacts',[]) if isinstance(x,dict) and x.get('id')}
        check(aids==pids, 'published artifact ids differ from AIM')
    case('R56_ARTIFACT_EQUIVALENCE', artifact_equivalence)

    def projection_equivalence():
        a=load_yaml(authoring/'ordo_projection.yaml')
        p=load_yaml(design/'playbook_projection.yaml')
        check(p.get('source_projection_sha256')==sha(authoring/'ordo_projection.yaml'), 'published projection not bound to current AIM projection hash')
        check(p.get('information_bindings')==a.get('information_bindings'), 'information bindings differ')
        check(p.get('group_bindings')==a.get('group_bindings'), 'group bindings differ')
    case('R57_ORDO_PROJECTION_EQUIVALENCE', projection_equivalence)

    def archive_complete():
        req={'MODEL_BUNDLE.yaml','information_dependency_graph.yaml','variable_catalog.yaml','variable_group_catalog.yaml','artifact_catalog.yaml','playbook_projection.yaml'}
        with zipfile.ZipFile(design/'DATA_FLOW_PACKAGE.zip') as z:
            names={n.rstrip('/') for n in z.namelist() if not n.endswith('/')}
        check(req<=names, f'data flow archive missing {sorted(req-names)}')
    case('R58_DATA_FLOW_PACKAGE_COMPLETENESS', archive_complete)

    def editor_discoverable_shape():
        b=load_yaml(design/'MODEL_BUNDLE.yaml')
        c=b.get('canonical_sources') or {}
        gp=design/str(c.get('graph') or '')
        g=load_yaml(gp)
        check(isinstance(g.get('nodes'),list) and isinstance(g.get('edges'),list), 'Editor contract requires graph nodes[] and edges[]')
        for key in ('variable_catalog','variable_group_catalog','artifact_catalog','playbook_projection'):
            ref=c.get(key); check(ref and (design/ref).is_file(), f'Editor canonical source {key} unresolved')
    case('R59_EDITOR_SOURCE_DATA_FLOW_DISCOVERABLE_SHAPE', editor_discoverable_shape)

    def generated_hashes():
        b=load_yaml(design/'MODEL_BUNDLE.yaml')
        up=b.get('upstream_sha256') or {}
        expected={
          'information_object_catalog.yaml':sha(authoring/'information_object_catalog.yaml'),
          'information_group_catalog.yaml':sha(authoring/'information_group_catalog.yaml'),
          'information_flow_graph.yaml':sha(authoring/'information_flow_graph.yaml'),
          'artifact_catalog.yaml':sha(authoring/'artifact_catalog.yaml'),
          'ordo_projection.yaml':sha(authoring/'ordo_projection.yaml'),
        }
        check(up==expected, 'MODEL_BUNDLE upstream hashes do not match canonical AIM')
    case('R60_PUBLICATION_PROVENANCE_HASHES', generated_hashes)

    passed=sum(1 for _,ok,_ in results if ok)
    for name,ok,msg in results:
        print(('PASS' if ok else 'FAIL'), name, ('' if ok else ':: '+msg))
    print(json.dumps({'passed':passed,'total':len(results),'failed':len(results)-passed}, sort_keys=True))
    return 0 if passed==len(results) else 1

if __name__=='__main__':
    raise SystemExit(main())
