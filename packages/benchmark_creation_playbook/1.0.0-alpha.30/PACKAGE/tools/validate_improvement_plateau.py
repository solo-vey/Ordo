#!/usr/bin/env python3
import argparse,json,hashlib,sys
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument("report"); a=p.parse_args(); d=json.load(open(a.report))
 req=["baseline","candidate","material_improvements","protected_regressions","decision","next_route"]
 errs=[f"missing:{k}" for k in req if k not in d]
 decision=d.get("decision")
 if decision=="ACCEPT_IMPROVED":
  if not d.get("material_improvements"): errs.append("accepted_without_material_improvement")
  if d.get("protected_regressions"): errs.append("accepted_with_protected_regression")
 elif decision in ("REJECT_PLATEAU","REJECT_REGRESSION"):
  if d.get("baseline",{}).get("sha256_after") != d.get("baseline",{}).get("sha256_before"): errs.append("baseline_not_retained")
 else: errs.append("invalid_decision")
 if d.get("retry",{}).get("same_strategy") and not any(d.get("retry",{}).get(k) for k in ("new_defect_evidence","new_facts","changed_strategy")):
  errs.append("unauthorized_identical_retry")
 out={"status":"PASS" if not errs else "FAIL","errors":errs}
 print(json.dumps(out,indent=2)); return 0 if not errs else 1
if __name__=="__main__": raise SystemExit(main())
