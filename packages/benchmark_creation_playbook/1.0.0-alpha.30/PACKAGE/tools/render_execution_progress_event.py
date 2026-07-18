#!/usr/bin/env python3
import argparse,json,re,sys,yaml
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument("event");p.add_argument("--registry",default="EXECUTION_PROGRESS_STATUS_REGISTRY.yaml");a=p.parse_args()
 e=json.loads(Path(a.event).read_text()); r=yaml.safe_load(Path(a.registry).read_text()); allowed={x["id"] for x in r["statuses"]}
 req=["event_id","run_id","step_id","step_sequence","attempt","short_summary","status","authoritative_evidence_refs","emitted_at","language","informational_only"]
 errors=[f"missing:{k}" for k in req if k not in e]
 if e.get("status") not in allowed: errors.append("unregistered_status")
 if e.get("informational_only") is not True: errors.append("not_informational_only")
 if not e.get("authoritative_evidence_refs"): errors.append("unbound_event")
 text=(e.get("short_summary","")+" "+e.get("reason","")).lower()
 forbidden=["chain of thought","internal reasoning","я думаю крок за кроком","приховані міркування"]
 if any(x in text for x in forbidden): errors.append("reasoning_disclosure")
 if "\n" in e.get("short_summary","") or "\n" in e.get("reason",""): errors.append("not_single_line")
 if errors:
  print(json.dumps({"status":"PROGRESS_EVENT_SUPPRESSED","errors":errors},ensure_ascii=False)); return 2
 line=f"Крок {e['step_id']} — {e['short_summary']} — {e['status']}"
 if e.get("reason"): line+=f": {e['reason']}"
 print(line); return 0
if __name__=="__main__": raise SystemExit(main())
