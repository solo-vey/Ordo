#!/usr/bin/env python3
import argparse,json
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('-o','--output'); a=ap.parse_args()
d=json.load(open(a.input)); src=d.get('defects',d if isinstance(d,list) else [])
allowed=('id','severity','dimension','candidate_problem','candidate_evidence','why_it_matters','remediation','remediation_target','points')
out=[]
for x in src:
    y={k:x[k] for k in allowed if k in x}
    y['reference_text_exposed']=False
    out.append(y)
res={'sanitized_defects':out}
s=json.dumps(res,ensure_ascii=False,indent=2)
if a.output: Path(a.output).write_text(s+'\n')
else: print(s)
