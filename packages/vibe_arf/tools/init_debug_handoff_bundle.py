#!/usr/bin/env python3
from pathlib import Path
import json, datetime, argparse

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--session-id',default=None)
    a=ap.parse_args(); root=Path(a.root).resolve(); d=root/'debug_handoff'/'working'; d.mkdir(parents=True,exist_ok=True)
    manifest=d/'session_manifest.json'
    if manifest.exists():
        data=json.loads(manifest.read_text())
    else:
        sid=a.session_id or ('session-'+datetime.datetime.now().strftime('%Y%m%dT%H%M%S'))
        data={'schema_version':'1.0','session_id':sid,'started_at':now(),'mode':'debug_handoff_visible','status':'IN_PROGRESS','intermediate_revisions':[],'problems':[],'repairs':[],'tests':[],'gate_history':[],'artifact_lineage':[]}
        manifest.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    p=d/'progress_events.jsonl'; p.touch(exist_ok=True)
    print(manifest)
if __name__=='__main__': main()
