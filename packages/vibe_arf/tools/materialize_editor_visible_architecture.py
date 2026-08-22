#!/usr/bin/env python3
from pathlib import Path
import argparse,json,yaml

def build(root):
    groups=(yaml.safe_load((root/'authoring/information_group_catalog.yaml').read_text()) or {}).get('groups',[])
    objs=(yaml.safe_load((root/'authoring/information_object_catalog.yaml').read_text()) or {}).get('objects',[])
    flow=(yaml.safe_load((root/'authoring/information_flow_graph.yaml').read_text()) or {}).get('edges',[])
    proj=(yaml.safe_load((root/'authoring/ordo_projection.yaml').read_text()) or {}).get('information_bindings',[])
    arts=(yaml.safe_load((root/'authoring/artifact_catalog.yaml').read_text()) or {}).get('artifacts',[])
    surface={'schema_version':'1.0','surface_id':'VIBE_EDITOR_ARCHITECTURE_SURFACE','canonical_sources':{'groups':'authoring/information_group_catalog.yaml','variables':'authoring/information_object_catalog.yaml','dataflow':'authoring/information_flow_graph.yaml','bindings':'authoring/ordo_projection.yaml','artifacts':'authoring/artifact_catalog.yaml'},
      'groups':[{'id':x['id'],'title':x.get('title'),'members':x.get('members',[])} for x in groups],
      'variables':[{'id':x['id'],'group_id':x.get('group_id'),'kind':x.get('kind'),'origins':x.get('origins',[]),'consumers':x.get('consumers',[])} for x in objs],
      'dataflow_edges':[{'from':x.get('from'),'to':x.get('to'),'type':x.get('type')} for x in flow],
      'bindings':[{'information_id':x.get('information_id'),'node_ids':x.get('node_ids',[]),'status':x.get('status')} for x in proj],
      'materialization':[{'artifact_id':x['id'],'kind':x.get('kind'),'inputs':x.get('inputs',[]),'lifecycle':x.get('lifecycle'),'verification_required':bool((x.get('verification') or {}).get('required'))} for x in arts]}
    pkg=next((x for x in arts if x['id']=='A_GENERATED_PLAYBOOK_PACKAGE'),None)
    surface['archive_path']={'artifact_id':'A_GENERATED_PLAYBOOK_PACKAGE','inputs':pkg.get('inputs',[]) if pkg else [],'path_chain':['A_GENERATED_PLAYBOOK_SOURCE','A_VERIFICATION_EVIDENCE','A_GENERATED_PLAYBOOK_PACKAGE','A_DELIVERY_HANDOFF']}
    return surface

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); a=ap.parse_args(); root=Path(a.root).resolve(); s=build(root); p=root/'editor/architecture_surface.json'; p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'status':'PASS','path':str(p),'groups':len(s['groups']),'variables':len(s['variables']),'dataflow_edges':len(s['dataflow_edges']),'bindings':len(s['bindings']),'materialization':len(s['materialization'])},indent=2))
if __name__=='__main__': main()
