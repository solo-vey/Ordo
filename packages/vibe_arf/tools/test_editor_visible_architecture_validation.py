#!/usr/bin/env python3
from pathlib import Path
import json, yaml, importlib.util
R=Path(__file__).resolve().parents[1]
results=[]; failures=[]
def check(i,fn):
    try: fn(); results.append({'id':i,'status':'PASS'})
    except Exception as e: failures.append({'id':i,'error':f'{type(e).__name__}: {e}'}); results.append({'id':i,'status':'FAIL','error':f'{type(e).__name__}: {e}'})

def read_json(rel): return json.loads((R/rel).read_text())
def read_yaml(rel): return yaml.safe_load((R/rel).read_text())

def policy_present():
    d=read_json('source/editor-visible-architecture-policy.json')
    assert d['contract_id']=='VIBE_EDITOR_VISIBLE_ARCHITECTURE_V1'
    assert d['required_surfaces']==['groups','variables','dataflow_edges','bindings','materialization','archive_path']
    assert d['zip_presence_is_insufficient'] is True

def law_present():
    t=(R/'PLAYBOOK_LAWS.md').read_text()
    assert 'E51_EDITOR_VISIBLE_ARCHITECTURE' in t
    assert 'reconstructible in the Editor' in t

def surface_manifest_present():
    d=read_json('editor/architecture_surface.json')
    assert d['schema_version']=='1.0'
    for k in ['groups','variables','dataflow_edges','bindings','materialization','archive_path']:
        assert k in d and d[k], k

def surface_manifest_crosschecks_canonical_data():
    surf=read_json('editor/architecture_surface.json')
    groups=read_yaml('authoring/information_group_catalog.yaml')['groups']
    objs=read_yaml('authoring/information_object_catalog.yaml')['objects']
    flow=read_yaml('authoring/information_flow_graph.yaml')
    proj=read_yaml('authoring/ordo_projection.yaml')['information_bindings']
    assert {g['id'] for g in groups} <= {g['id'] for g in surf['groups']}
    assert {o['id'] for o in objs} <= {v['id'] for v in surf['variables']}
    assert len(surf['dataflow_edges']) >= len(flow.get('edges',[]))
    assert {b['information_id'] for b in proj} <= {b['information_id'] for b in surf['bindings']}

def materialization_archive_are_explicit():
    s=read_json('editor/architecture_surface.json')
    mats=s['materialization']
    assert any(x.get('artifact_id')=='A_GENERATED_PLAYBOOK_SOURCE' for x in mats)
    assert any(x.get('artifact_id')=='A_GENERATED_PLAYBOOK_PACKAGE' for x in mats)
    a=s['archive_path']
    assert a.get('artifact_id')=='A_GENERATED_PLAYBOOK_PACKAGE'
    assert a.get('path_chain') and len(a['path_chain']) >= 2

def validator_exists_and_passes():
    p=R/'tools/validate_editor_visible_architecture.py'; assert p.exists()
    spec=importlib.util.spec_from_file_location('ev',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    out=m.validate(R)
    assert out['status']=='PASS', out
    assert out['surface_reconstructible'] is True

def editor_adapter_loads_surface():
    p=R/'utilities/ordo_tree_editor/editor_service.py'; text=p.read_text()
    assert 'architecture_surface' in text
    assert '/api/architecture-surface' in text
    spec=importlib.util.spec_from_file_location('editor_service_ev',p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    data=m.load_architecture_surface(R)
    assert data['groups'] and data['variables'] and data['bindings']

def editor_ui_renders_surface():
    html=(R/'utilities/ordo_tree_editor/web/index.html').read_text()
    js=(R/'utilities/ordo_tree_editor/web/app.js').read_text()
    assert 'architecture-surface' in html
    assert '/api/architecture-surface' in js
    for word in ['Groups','Variables','Bindings','Materialization','Archive path']:
        assert word in js or word in html, word

def data_layer_contract_present():
    objs=read_yaml('authoring/information_object_catalog.yaml')['objects']
    assert any(x.get('id')=='I_EDITOR_VISIBLE_ARCHITECTURE_CONTRACT' for x in objs)
    groups=read_yaml('authoring/information_group_catalog.yaml')['groups']
    assert any('I_EDITOR_VISIBLE_ARCHITECTURE_CONTRACT' in g.get('members',[]) for g in groups)
    proj=read_yaml('authoring/ordo_projection.yaml')['information_bindings']
    assert any(x.get('information_id')=='I_EDITOR_VISIBLE_ARCHITECTURE_CONTRACT' for x in proj)

for i,f in [
('EV1_POLICY',policy_present),('EV2_LAW',law_present),('EV3_SURFACE_MANIFEST',surface_manifest_present),('EV4_CANONICAL_CROSSCHECK',surface_manifest_crosschecks_canonical_data),('EV5_MATERIALIZATION_ARCHIVE',materialization_archive_are_explicit),('EV6_VALIDATOR',validator_exists_and_passes),('EV7_EDITOR_ADAPTER',editor_adapter_loads_surface),('EV8_EDITOR_UI',editor_ui_renders_surface),('EV9_DATA_LAYER',data_layer_contract_present)]: check(i,f)
print(json.dumps({'status':'PASS' if not failures else 'FAIL','tests_total':len(results),'passed':sum(r['status']=='PASS' for r in results),'failed':len(failures),'results':results},indent=2))
raise SystemExit(0 if not failures else 1)
