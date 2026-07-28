#!/usr/bin/env python3
import argparse,yaml
from pathlib import Path
RANK={"must_not":4,"must":3,"should":2,"may":1,"unknown":0}
def key(p): return (p.get("subject"),p.get("condition"),p.get("predicate"),p.get("effect"),p.get("route"))
def load(p): return yaml.safe_load(Path(p).read_text(encoding="utf-8"))
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--baseline",required=True);ap.add_argument("--candidate",required=True);ap.add_argument("--output",required=True);a=ap.parse_args()
 b=load(a.baseline);c=load(a.candidate);bi={key(p):p for p in b.get("propositions",[])};ci={key(p):p for p in c.get("propositions",[])};changes=[]
 for k,bp in bi.items():
  cp=ci.get(k)
  if cp is None:
   block=bp.get("strength") in ("must","must_not");changes.append({"classification":"semantic_missing","baseline_ids":[bp["id"]],"candidate_ids":[],"reason":"baseline proposition missing","blocking":block});continue
  br,cr=RANK.get(bp.get("strength","unknown"),0),RANK.get(cp.get("strength","unknown"),0)
  cls="semantic_strengthened" if cr>br else "semantic_weakened" if cr<br else "semantic_preserved"
  changes.append({"classification":cls,"baseline_ids":[bp["id"]],"candidate_ids":[cp["id"]],"reason":"matched normalized proposition","blocking":cls=="semantic_weakened" and bp.get("strength") in ("must","must_not")})
 for k,cp in ci.items():
  if k not in bi: changes.append({"classification":"semantic_added","baseline_ids":[],"candidate_ids":[cp["id"]],"reason":"candidate proposition added","blocking":False})
 out={"schema":"ordo.prh.semantic_projection_diff.v1","baseline":b.get("package_identity",{}),"candidate":c.get("package_identity",{}),"changes":changes,"verdict":"FAIL" if any(x["blocking"] for x in changes) else "PASS"}
 Path(a.output).write_text(yaml.safe_dump(out,sort_keys=False,allow_unicode=True),encoding="utf-8")
if __name__=="__main__": main()
