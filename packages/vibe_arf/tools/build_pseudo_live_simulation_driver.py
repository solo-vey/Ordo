#!/usr/bin/env python3
from pathlib import Path
import argparse,json,yaml

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('evidence'); ap.add_argument('out'); ap.add_argument('--scenario',default='PSEUDO_LIVE'); a=ap.parse_args()
 d=json.loads(Path(a.evidence).read_text())
 if d.get('execution_mode')!='PSEUDO_LIVE_OPTIMIZATION': raise SystemExit('evidence is not pseudo-live')
 responses={}
 for c in d.get('model_calls') or []:
  node=c.get('element_id'); payload=c.get('parsed_response',c.get('raw_response'))
  if not node: raise SystemExit('element_id required')
  responses.setdefault(node,{}).setdefault('respond',[]).append(payload if isinstance(payload,dict) else {'value':payload})
 out={'format':'ordo-simulation-model-responses/v0.1','scenario':a.scenario,'responses':responses,'x_vibe_provenance':{'execution_mode':'PSEUDO_LIVE_OPTIMIZATION','evidence_file':str(Path(a.evidence).name)}}
 Path(a.out).write_text(yaml.safe_dump(out,sort_keys=False,allow_unicode=True),encoding='utf-8')
 print(json.dumps({'status':'PASS','nodes':len(responses),'out':a.out}))
if __name__=='__main__': main()
