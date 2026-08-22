#!/usr/bin/env python3
from pathlib import Path
import argparse, json, yaml, sys, re
from instantiate_data_layer_pattern import canonical_digest
from materialize_pattern_data_layer_expansion import expand
from derive_pattern_execution_projection import derive
from pattern_template_semantics import execution_components, canonical_outcome_edges
from pattern_data_layer_semantics import data_roles

def ids_from(root):
    objs=yaml.safe_load((root/'authoring/information_object_catalog.yaml').read_text()) or {}
    arts=yaml.safe_load((root/'authoring/artifact_catalog.yaml').read_text()) or {}
    return {x['id'] for x in objs.get('objects',[])},{x['id'] for x in arts.get('artifacts',[])}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--phase',choices=['early','merged'],default='merged'); a=ap.parse_args(); root=Path(a.root).resolve()
    reg=json.loads((root/'patterns/PATTERN_REGISTRY.json').read_text()); valid={(x['id'],str(x['version'])) for x in reg.get('patterns',[])}
    cat=yaml.safe_load((root/'authoring/pattern_instance_catalog.yaml').read_text()) or {}; objs,arts=ids_from(root); failures=[]
    for inst in cat.get('instances',[]):
        iid=inst.get('instance_id','?'); pid=inst.get('pattern_id'); ver=str(inst.get('pattern_version'))
        if (pid,ver) not in valid: failures.append(f'{iid}: unknown pattern/version'); continue
        if 'execution_projection' in inst: failures.append(f'{iid}: canonical Data Layer must not contain execution projection/node ids')
        if re.search(r'\b[NG]_[A-Z0-9_]+\b',json.dumps(inst)): failures.append(f'{iid}: canonical Data Layer contains concrete graph ids')
        pdef=yaml.safe_load((root/'patterns'/pid/'PATTERN.yaml').read_text()) or {}
        dl=yaml.safe_load((root/'patterns'/pid/'DATA_LAYER.template.yaml').read_text()) or {}
        required={x['role']:x.get('binds_to') for x in data_roles(dl) if x.get('required',True)}
        b=inst.get('data_layer_bindings',{})
        missing=sorted(set(required)-set(b))
        if missing: failures.append(f'{iid}: missing data roles {missing}')
        if inst.get('requirement_origin') in (None,'','pattern_instantiation','pattern_generated'):
            failures.append(f'{iid}: reward-safe preexisting requirement origin missing')
        allowed_ext=set((pdef.get('extension_policy') or {}).get('allowed',[]))
        for ov in inst.get('local_overrides') or []:
            if isinstance(ov,dict) and ov.get('extension_point') not in allowed_ext:
                failures.append(f"{iid}: forbidden extension point {ov.get('extension_point')}")
        if a.phase=='merged':
            for role,target in b.items():
                typ=required.get(role,''); vals=target if isinstance(target,list) else [target]
                for v in vals:
                    if typ=='artifact' and v not in arts: failures.append(f'{iid}: {role} -> missing artifact {v}')
                    elif typ=='information' and v not in objs: failures.append(f'{iid}: {role} -> missing information {v}')
                    elif typ in ('artifact_or_information','information_or_artifact') and v not in arts|objs: failures.append(f'{iid}: {role} -> unresolved {v}')
        ex=yaml.safe_load((root/'patterns'/pid/'EXECUTION.template.yaml').read_text()) or {}
        roles=[x.get('role') for x in execution_components(ex)]
        if not roles or len(roles)!=len(set(roles)): failures.append(f'{iid}: invalid execution template component roles')
        edges=canonical_outcome_edges(ex)
        role_set=set(roles)
        for edge in edges:
            if edge.get('from_role') not in role_set:
                failures.append(f"{iid}: canonical outcome edge references unknown source role {edge}")
            target=edge.get('to_role')
            terminal=edge.get('terminal')
            if target not in role_set and not terminal:
                # Uppercase symbolic target is an explicit external terminal result in some pattern revisions.
                if not (isinstance(target,str) and target and target.upper()==target):
                    failures.append(f"{iid}: canonical outcome edge references unknown destination {edge}")
            if not edge.get('outcome'):
                failures.append(f"{iid}: canonical outcome edge lacks exact outcome token {edge}")
        expected=canonical_digest(root,pid,iid,b,inst.get('artifact_id'),inst.get('requirement_origin','preexisting_project_data_layer'))
        if inst.get('instance_digest')!=expected: failures.append(f'{iid}: instance digest mismatch')
    amap={x['id']:x for x in (yaml.safe_load((root/'authoring/artifact_catalog.yaml').read_text()) or {}).get('artifacts',[])}
    iids={i.get('instance_id') for i in cat.get('instances',[])}
    for aid,aobj in amap.items():
        pb=aobj.get('pattern_binding')
        if pb and pb.get('instance_id') not in iids: failures.append(f'{aid}: pattern binding instance missing')
    # Expansion must be reproducible from canonical Data Layer + library templates.
    expected_exp=expand(root)
    ep=root/'authoring/pattern_data_layer_expansion.yaml'
    if not ep.exists(): failures.append('missing pattern_data_layer_expansion.yaml')
    else:
        actual_exp=yaml.safe_load(ep.read_text()) or {}
        if actual_exp!=expected_exp: failures.append('pattern Data Layer expansion stale')
    if a.phase=='merged':
        flow=yaml.safe_load((root/'authoring/information_flow_graph.yaml').read_text()) or {}
        fedges={(e.get('from'),e.get('to'),e.get('type')) for e in flow.get('edges',[])}
        for mod in expected_exp.get('modules',[]):
            for e in mod.get('module_edges',[]):
                t=(e.get('from'),e.get('to'),e.get('type'))
                if t not in fedges: failures.append(f"{mod.get('pattern_instance_id')}: missing merged module edge {t}")
        # Execution projection exists only downstream of successful merged Data Layer and is exact-derived.
        pp=root/'authoring/pattern_execution_projection.yaml'
        if not pp.exists(): failures.append('missing pattern execution projection')
        else:
            actual=yaml.safe_load(pp.read_text()) or {}; expected_proj=derive(root)
            if actual!=expected_proj: failures.append('pattern execution projection stale or not template-derived')
    out={'status':'PASS' if not failures else 'FAIL','phase':a.phase,'instances':len(cat.get('instances',[])),'failures':failures}; print(json.dumps(out,indent=2)); sys.exit(1 if failures else 0)
if __name__=='__main__': main()
