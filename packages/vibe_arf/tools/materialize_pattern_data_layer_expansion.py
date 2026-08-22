#!/usr/bin/env python3
from pathlib import Path
import argparse, yaml, json, hashlib
from pattern_data_layer_semantics import data_roles, data_module_edges

def expand(root):
    cat=yaml.safe_load((root/'authoring/pattern_instance_catalog.yaml').read_text()) or {}
    mods=[]
    for inst in cat.get('instances',[]):
        pid=inst['pattern_id']; dl=yaml.safe_load((root/'patterns'/pid/'DATA_LAYER.template.yaml').read_text()) or {}
        b=inst.get('data_layer_bindings',{})
        objs=[]
        for role in data_roles(dl):
            val=b.get(role['role']); vals=val if isinstance(val,list) else ([val] if val is not None else [])
            objs.append({'role':role['role'],'binding_kind':role.get('binds_to'),'bound_ids':vals,'required':role.get('required',True),'resolved_by_project_data_layer':True if vals else False})
        edges=[]
        for e in data_module_edges(dl):
            av=b.get(e['from_role']); bv=b.get(e['to_role']); aa=av if isinstance(av,list) else ([av] if av is not None else []); bb=bv if isinstance(bv,list) else ([bv] if bv is not None else [])
            for a in aa:
                for z in bb: edges.append({'from':a,'to':z,'type':e['type'],'from_role':e['from_role'],'to_role':e['to_role']})
        mods.append({'pattern_instance_id':inst['instance_id'],'pattern_id':pid,'pattern_version':str(inst['pattern_version']),'instance_digest':inst['instance_digest'],'module_objects':objs,'module_edges':edges})
    payload={'schema_version':'1.0','source_of_truth':'authoring/pattern_instance_catalog.yaml + patterns/*/DATA_LAYER.template.yaml','modules':mods}
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode(); payload['expansion_digest']=hashlib.sha256(raw).hexdigest(); return payload

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--out'); a=ap.parse_args(); root=Path(a.root).resolve(); p=expand(root); out=Path(a.out) if a.out else root/'authoring/pattern_data_layer_expansion.yaml'; out.write_text(yaml.safe_dump(p,sort_keys=False,allow_unicode=True)); print(json.dumps({'status':'PASS','modules':len(p['modules']),'path':str(out),'expansion_digest':p['expansion_digest']},indent=2))
if __name__=='__main__': main()
