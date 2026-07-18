#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, sys
root=Path(__file__).resolve().parents[5]
validator=root/"tools"/"validate_post_generation_review.py"
cases=[
 ("valid_review.json",0),
 ("invalid_unsupported_claim.json",1),
 ("invalid_open_critical.json",1),
]
results=[]
for name,expected in cases:
 p=Path(__file__).parent/name
 r=subprocess.run([sys.executable,str(validator),str(p),"--root",str(root)],capture_output=True,text=True)
 results.append({"case":name,"expected":expected,"actual":r.returncode,"passed":r.returncode==expected,"output":json.loads(r.stdout)})
print(json.dumps({"status":"PASS" if all(x["passed"] for x in results) else "FAIL","results":results},indent=2))
raise SystemExit(0 if all(x["passed"] for x in results) else 1)
