#!/usr/bin/env python3
from pathlib import Path
import argparse,json,yaml,hashlib

def build(root):
    arts=yaml.safe_load((root/'authoring/artifact_catalog.yaml').read_text()) or {}
    caps=yaml.safe_load((root/'authoring/capability_requirement_catalog.yaml').read_text()) or {}
    a=[]
    for x in arts.get('artifacts',[]):
        a.append({'id':x['id'],'kind':x.get('kind'),'required':bool((x.get('materialization') or {}).get('required',True)),'requirement_origin':x.get('requirement_origin'),'lifecycle':x.get('lifecycle')})
    c=[]
    for x in caps.get('requirements',[]):
        c.append({'id':x['id'],'capability_tag':x.get('capability_tag'),'artifact_id':x.get('artifact_id'),'required':bool(x.get('required',True)),'requirement_origin':x.get('requirement_origin')})
    payload={'schema_version':'1.0','freeze_phase':'before_pattern_library_lookup','artifacts':sorted(a,key=lambda z:z['id']),'capability_requirements':sorted(c,key=lambda z:z['id'])}
    raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode(); payload['snapshot_digest']=hashlib.sha256(raw).hexdigest(); return payload

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--out'); a=ap.parse_args(); root=Path(a.root).resolve(); p=build(root); out=Path(a.out) if a.out else root/'authoring/pattern_selection_input_snapshot.json'; out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({'status':'PASS','path':str(out),'artifacts':len(p['artifacts']),'capabilities':len(p['capability_requirements']),'snapshot_digest':p['snapshot_digest']},indent=2))
if __name__=='__main__': main()
