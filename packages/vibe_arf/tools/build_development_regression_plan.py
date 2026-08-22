#!/usr/bin/env python3
from pathlib import Path
import argparse,json
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("request"); ap.add_argument("--output",required=True); a=ap.parse_args()
 req=json.loads(Path(a.request).read_text())
 required=["change_id","change_class","protected_invariant","baseline_identity","regression_asset","prechange_status"]
 missing=[x for x in required if not req.get(x)]
 if missing:
  out={"status":"FAIL","reason":"MISSING_REQUIRED_FIELDS","missing":missing}
 else:
  impacted=sorted(dict.fromkeys(req.get("impacted_checks") or []))
  pre=req.get("prechange_status")
  acceptable=pre in {"FAIL","NOT_APPLICABLE"}
  out={"status":"PASS" if acceptable else "FAIL","change_id":req["change_id"],"change_class":req["change_class"],"protected_invariant":req["protected_invariant"],"baseline_identity":req["baseline_identity"],"regression_asset":req["regression_asset"],"prechange_evidence":{"status":pre,"reason":req.get("prechange_reason")},"impacted_checks":impacted,"regression_proof":{"namespace":"REGRESSION_PROOF","status":"PRECHANGE_CAPTURED" if acceptable else "INVALID"},"live_proof":{"namespace":"LIVE_PROOF","status":"NOT_RUN"}}
 Path(a.output).write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps(out,indent=2)); return 0 if out["status"]=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())
