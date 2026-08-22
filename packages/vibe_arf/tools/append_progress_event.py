#!/usr/bin/env python3
from pathlib import Path
import json, datetime, argparse
VALID={'stage_start','node_enter','gate_result','repair_or_route','checkpoint'}
def now(): return datetime.datetime.now(datetime.timezone.utc)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--event-type',required=True,choices=sorted(VALID)); ap.add_argument('--current-element',required=True); ap.add_argument('--summary',required=True); ap.add_argument('--next-action',required=True); ap.add_argument('--status',default=None); ap.add_argument('--visibility',choices=['visible','hidden'],default='visible')
    a=ap.parse_args(); d=Path(a.root).resolve()/'debug_handoff'/'working'; d.mkdir(parents=True,exist_ok=True)
    if not (d/'session_manifest.json').exists(): raise SystemExit('debug handoff bundle not initialized')
    t=now(); ts=t.isoformat(); state_path=d/'visible_timing_state.json'; state={}
    if state_path.is_file():
        try: state=json.loads(state_path.read_text(encoding='utf-8'))
        except Exception: state={}
    e={'timestamp':ts,'event_type':a.event_type,'current_element':a.current_element,'summary':a.summary,'next_action':a.next_action,'visibility':a.visibility,'visible_baseline_advanced':False}
    if a.status: e['status']=a.status
    if a.visibility=='visible':
        prev=state.get('last_visible_timestamp'); delta=None
        if prev:
            try: delta=(t-datetime.datetime.fromisoformat(prev)).total_seconds()
            except Exception: delta=None
        e['elapsed_since_previous_visible_seconds']=delta
        state={'last_visible_timestamp':ts,'last_visible_element':a.current_element}
        state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); e['visible_baseline_advanced']=True
    else:
        e['elapsed_since_previous_visible_seconds']=None
    with (d/'progress_events.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(e,ensure_ascii=False)+'\n')
    print(json.dumps(e,ensure_ascii=False))
if __name__=='__main__': main()
