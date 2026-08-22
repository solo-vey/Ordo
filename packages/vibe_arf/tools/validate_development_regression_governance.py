#!/usr/bin/env python3
from pathlib import Path
import argparse,json
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("evidence"); a=ap.parse_args(); d=json.loads(Path(a.evidence).read_text())
 errs=[]
 if d.get("regression_proof",{}).get("namespace")!="REGRESSION_PROOF": errs.append("REGRESSION_PROOF_NAMESPACE")
 if d.get("live_proof",{}).get("namespace")!="LIVE_PROOF": errs.append("LIVE_PROOF_NAMESPACE")
 post=d.get("postchange_evidence",{})
 if post and post.get("regression_status")!="PASS": errs.append("POSTCHANGE_REGRESSION_NOT_PASS")
 if post and any(x.get("status")!="PASS" for x in post.get("impacted_checks",[])): errs.append("IMPACTED_CHECK_FAILED")
 out={"status":"FAIL" if errs else "PASS","errors":errs}
 print(json.dumps(out,indent=2)); return 1 if errs else 0
if __name__=="__main__": raise SystemExit(main())
