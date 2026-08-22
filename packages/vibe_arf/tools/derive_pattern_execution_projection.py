#!/usr/bin/env python3
from pathlib import Path
import argparse, yaml, hashlib, json, re, sys
from pattern_template_semantics import execution_components, canonical_outcome_edges
from pattern_data_layer_semantics import data_roles

CANONICAL_DATA_LAYER_INPUTS = [
    'authoring/information_object_catalog.yaml',
    'authoring/information_group_catalog.yaml',
    'authoring/artifact_catalog.yaml',
    'authoring/information_flow_graph.yaml',
    'authoring/interaction_projection.yaml',
    'authoring/capability_requirement_catalog.yaml',
    'authoring/pattern_instance_catalog.yaml',
]

def canonical_data_layer_digest(root):
    h=hashlib.sha256()
    for rel in CANONICAL_DATA_LAYER_INPUTS:
        p=root/rel
        if not p.exists(): raise FileNotFoundError(rel)
        h.update(rel.encode('utf-8')+b'\0'+hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()

def safe(s): return re.sub(r'[^A-Z0-9]+','_',str(s).upper()).strip('_')
def component_id(instance_id, role, kind):
    prefix='G' if kind=='gate' else 'N'
    return f"{prefix}_{safe(instance_id)}_{safe(role)}"


def merged_preconditions(root):
    failures=[]
    cat=yaml.safe_load((root/'authoring/pattern_instance_catalog.yaml').read_text()) or {}
    objs={x['id'] for x in (yaml.safe_load((root/'authoring/information_object_catalog.yaml').read_text()) or {}).get('objects',[])}
    arts={x['id'] for x in (yaml.safe_load((root/'authoring/artifact_catalog.yaml').read_text()) or {}).get('artifacts',[])}
    flow=yaml.safe_load((root/'authoring/information_flow_graph.yaml').read_text()) or {}
    fedges={(e.get('from'),e.get('to'),e.get('type')) for e in flow.get('edges',[])}
    exp=yaml.safe_load((root/'authoring/pattern_data_layer_expansion.yaml').read_text()) or {}
    modules={m.get('pattern_instance_id'):m for m in exp.get('modules',[])}
    for inst in cat.get('instances',[]):
        iid=inst.get('instance_id'); pid=inst.get('pattern_id')
        dl=yaml.safe_load((root/'patterns'/pid/'DATA_LAYER.template.yaml').read_text()) or {}
        role_types={x.get('role'):x.get('binds_to') for x in data_roles(dl) if x.get('required',True)}
        for role,target in (inst.get('data_layer_bindings') or {}).items():
            vals=target if isinstance(target,list) else [target]; typ=role_types.get(role)
            for v in vals:
                if typ=='artifact' and v not in arts: failures.append(f'{iid}: unresolved artifact binding {role}={v}')
                elif typ=='information' and v not in objs: failures.append(f'{iid}: unresolved information binding {role}={v}')
                elif typ in ('artifact_or_information','information_or_artifact') and v not in (objs|arts): failures.append(f'{iid}: unresolved semantic binding {role}={v}')
        mod=modules.get(iid)
        if not mod: failures.append(f'{iid}: missing Data-Layer expansion module'); continue
        for e in mod.get('module_edges',[]):
            t=(e.get('from'),e.get('to'),e.get('type'))
            if t not in fedges: failures.append(f'{iid}: Data-Layer module edge not merged {t}')
    return failures

def derive(root):
    cat=yaml.safe_load((root/'authoring/pattern_instance_catalog.yaml').read_text()) or {}; frags=[]
    for i in cat.get('instances',[]):
        pid=i['pattern_id']; ex=yaml.safe_load((root/'patterns'/pid/'EXECUTION.template.yaml').read_text()) or {}
        comps=[]; ids={}
        for c in execution_components(ex):
            cid=component_id(i['instance_id'],c['role'],c['kind']); ids[c['role']]=cid
            comps.append({'role':c['role'],'component_id':cid,'kind':c['kind'],'responsibility_class':c.get('responsibility_class'),'data_layer_instance_id':i['instance_id']})
        edges=[]
        for e in canonical_outcome_edges(ex):
            row={'from':ids[e['from_role']],'type':e.get('type','canonical_outcome'),'outcome':e.get('outcome','NEXT')}
            target_role=e.get('to_role')
            if target_role in ids:
                row['to']=ids[target_role]
                row['to_role']=target_role
            else:
                terminal=e.get('terminal') or target_role
                if terminal:
                    row['terminal']=terminal
            edges.append(row)
        frags.append({'pattern_instance_id':i['instance_id'],'pattern_id':pid,'pattern_version':str(i['pattern_version']),'instance_digest':i['instance_digest'],'artifact_id':i.get('artifact_id'),
                      'projection_source':'pattern_execution_template','selection_performed_at_tree_stage':False,'components':comps,'edges':edges})
    payload={'schema_version':'1.2','source_of_truth':'authoring/pattern_instance_catalog.yaml','projection_policy':'derive_only_no_tree_reselection','canonical_data_layer_inputs':list(CANONICAL_DATA_LAYER_INPUTS),'canonical_data_layer_digest':canonical_data_layer_digest(root),'fragments':frags}
    canonical=json.dumps(payload,sort_keys=True,separators=(',',':')).encode(); payload['projection_digest']=hashlib.sha256(canonical).hexdigest()
    return payload

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--out'); a=ap.parse_args(); root=Path(a.root).resolve(); failures=merged_preconditions(root)
    if failures:
        print(json.dumps({'status':'FAIL','code':'PATTERN_DATA_LAYER_NOT_MERGED','failures':failures},indent=2)); raise SystemExit(2)
    payload=derive(root)
    out=Path(a.out) if a.out else root/'authoring/pattern_execution_projection.yaml'; out.write_text(yaml.safe_dump(payload,sort_keys=False,allow_unicode=True)); print(json.dumps({'status':'PASS','fragments':len(payload['fragments']),'path':str(out),'projection_digest':payload['projection_digest']},indent=2))
if __name__=='__main__': main()
