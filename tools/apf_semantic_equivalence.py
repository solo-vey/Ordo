#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

VOLATILE_TOP = {"compiled_at", "security"}
VOLATILE_OP_FIELDS = {"question"}

def normalize_ir(data: dict[str, Any]) -> dict[str, Any]:
    out = {k: v for k, v in data.items() if k not in VOLATILE_TOP}
    ops=[]
    for op in out.get("ops", []):
        x=dict(op)
        if x.get("canary") is True:
            x["question"]="<CANARY_SECRET>"
        ops.append(x)
    ops.sort(key=lambda x:(str(x.get("op","")), str(x.get("id",""))))
    out["ops"]=ops
    return out

def digest(data: dict[str, Any]) -> str:
    raw=json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def index_ops(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {f"{o.get('op')}::{o.get('id')}":o for o in data.get("ops", [])}

def compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    a,b=normalize_ir(left),normalize_ir(right)
    ai,bi=index_ops(a),index_ops(b)
    added=sorted(set(bi)-set(ai)); removed=sorted(set(ai)-set(bi))
    changed=[]
    for key in sorted(set(ai)&set(bi)):
        if ai[key] != bi[key]: changed.append(key)
    equivalent=(a.get("package")==b.get("package") and a.get("ordo_version")==b.get("ordo_version") and not added and not removed and not changed)
    return {
      "kind":"apf_semantic_equivalence_report",
      "status":"passed" if equivalent else "failed",
      "equivalent":equivalent,
      "left_digest":digest(a), "right_digest":digest(b),
      "package_equal":a.get("package")==b.get("package"),
      "ordo_version_equal":a.get("ordo_version")==b.get("ordo_version"),
      "ops_left":len(ai), "ops_right":len(bi),
      "added_ops":added, "removed_ops":removed, "changed_ops":changed,
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("left"); ap.add_argument("right"); ap.add_argument("--out")
    ns=ap.parse_args()
    report=compare(json.loads(Path(ns.left).read_text()), json.loads(Path(ns.right).read_text()))
    text=json.dumps(report, indent=2, ensure_ascii=False)+"\n"
    if ns.out: Path(ns.out).write_text(text)
    print(text,end="")
    return 0 if report["equivalent"] else 1
if __name__=="__main__": raise SystemExit(main())
