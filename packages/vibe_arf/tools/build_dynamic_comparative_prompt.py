#!/usr/bin/env python3
import argparse,json
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument('input'); ap.add_argument('-o','--output'); a=ap.parse_args()
d=json.load(open(a.input))
refs=d.get('reference_profile',{}).get('references',d.get('references',[]))
# Only IDs/weights/reasons are included; never reference contents.
ref_public=[{k:r.get(k) for k in ('id','reference_id','relevance_weight','weight','relevance_reasons','relevance_reason') if k in r} for r in refs]
out={'role':'independent comparative evaluator','artifact_profile':d.get('artifact_profile',{}),'quality_dimensions':d.get('quality_dimensions',[]),'reference_profile':ref_public,'instructions':['perform fresh comparative discovery from scratch','do not use previous score or target score','do not assume previous defect backlog is complete','do not repair candidate','do not require literal copying','emit evidence-grounded defects and remediation','surface reference conflicts explicitly']}
s=json.dumps(out,ensure_ascii=False,indent=2)
if a.output: Path(a.output).write_text(s+'\n')
else: print(s)
