#!/usr/bin/env python3
from pathlib import Path
import argparse, json, yaml, hashlib

def canonical_digest(root,pid,instance_id,data_bindings,artifact_id=None,requirement_origin='preexisting_project_data_layer'):
    base=root/'patterns'/pid
    h=hashlib.sha256()
    for n in ['PATTERN.yaml','DATA_LAYER.template.yaml','EXECUTION.template.yaml']:
        h.update((base/n).read_bytes())
    payload={'pattern_id':pid,'instance_id':instance_id,'artifact_id':artifact_id,'data_layer_bindings':data_bindings,'requirement_origin':requirement_origin}
    h.update(json.dumps(payload,sort_keys=True,separators=(',',':')).encode())
    return h.hexdigest()

def build(root,pid,instance_id,data_bindings,artifact_id=None,selection_status='exact_fit_auto_instantiated',requirement_origin='preexisting_project_data_layer'):
    p=yaml.safe_load((root/'patterns'/pid/'PATTERN.yaml').read_text())['pattern']
    return {'instance_id':instance_id,'pattern_id':pid,'pattern_version':str(p['version']),'artifact_id':artifact_id,
            'selection_phase':'data_layer_authoring','selection_status':selection_status,
            'requirement_origin':requirement_origin,'data_layer_bindings':data_bindings,
            'projection_contract':'patterns/<pattern_id>/EXECUTION.template.yaml + this semantic binding',
            'local_overrides':[],'instance_digest':canonical_digest(root,pid,instance_id,data_bindings,artifact_id,requirement_origin)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--pattern',required=True); ap.add_argument('--instance',required=True); ap.add_argument('--artifact'); ap.add_argument('--data-bindings-json',required=True); ap.add_argument('--selection-status',default='exact_fit_auto_instantiated'); ap.add_argument('--requirement-origin',default='preexisting_project_data_layer'); ap.add_argument('--out')
    a=ap.parse_args(); root=Path(a.root).resolve(); inst=build(root,a.pattern,a.instance,json.loads(a.data_bindings_json),a.artifact,a.selection_status,a.requirement_origin)
    text=yaml.safe_dump(inst,sort_keys=False,allow_unicode=True)
    if a.out: Path(a.out).write_text(text)
    else: print(text,end='')
if __name__=='__main__': main()
