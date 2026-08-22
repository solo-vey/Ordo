#!/usr/bin/env python3
from pathlib import Path
import argparse,json,statistics

def rows(p):
 if not p.exists(): return []
 out=[]
 for line in p.read_text(errors='replace').splitlines():
  try: out.append(json.loads(line))
  except Exception: pass
 return out

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); ap.add_argument('--output',default=None); a=ap.parse_args(); r=Path(a.root).resolve()
 receipts=rows(r/'runtime/evidence/EXECUTION_RECEIPTS.jsonl'); timings=rows(r/'reports/AUTHORING_EXECUTION_TIMING.jsonl'); progress=rows(r/'debug_handoff/working/progress_events.jsonl')
 counts={}
 for x in receipts: counts[x.get('from_node')]=counts.get(x.get('from_node'),0)+1
 durations={}
 for x in timings:
  k=x.get('operation_id') or x.get('node_id') or 'unknown'; durations[k]=durations.get(k,0)+float(x.get('duration_ms') or 0)
 ranked=sorted(set(counts)|set(durations),key=lambda k:(durations.get(k,0),counts.get(k,0)),reverse=True)
 report={'status':'PASS','report':{'receipt_count':len(receipts),'timing_event_count':len(timings),'progress_event_count':len(progress),'execution_counts':counts,'duration_ms_by_operation':durations,'hotspot_ranking':ranked[:10],'token_count_source':'UNAVAILABLE' if not any('input_tokens' in x or 'output_tokens' in x for x in timings) else 'MIXED_OR_RECORDED','context_accounting':{'filesystem_scanned_bytes':None,'tool_output_visible_bytes':None,'model_loaded_content_bytes':None,'platform_overhead_tokens':None,'playbook_controlled_tokens':None,'unavailable_reason':'populate from runtime-observable host/tool evidence; do not infer from filesystem scans'}},'state_updates':{'performance_telemetry':{'execution_counts':counts,'duration_ms_by_operation':durations,'hotspot_ranking':ranked[:10]}}}
 out=Path(a.output) if a.output else r/'reports/OBSERVABILITY_DEBUG_SUMMARY.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__': main()
