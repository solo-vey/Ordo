#!/usr/bin/env python3
from __future__ import annotations
import argparse, fnmatch, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import yaml
DEFAULT_POLICY=Path("policies/english_only_policy.yaml")
def _now(): return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
def _matches(path,pattern):
    if pattern.endswith("/**"):
        prefix=pattern[:-3]
        return path==prefix or path.startswith(prefix+"/")
    return fnmatch.fnmatchcase(path,pattern)
def _walk(v,path=()):
    if isinstance(v,dict):
        for k,c in v.items(): yield from _walk(c,path+(str(k),))
    elif isinstance(v,list):
        for i,c in enumerate(v): yield from _walk(c,path+(str(i),))
    elif isinstance(v,str): yield "/".join(path),v
def _file_ex(rel,p):
    for item in p.get("path_exemptions",[]):
        if _matches(rel,item["glob"]): return item
    for item in p.get("file_exemptions",[]):
        if rel==item["path"]: return item
def _value_ex(field,rel,p):
    for pattern in p.get("language_fixture_globs",[]):
        if _matches(rel,pattern): return {"id":"language_behavior_fixture"}
    seg=field.split("/") if field else []
    for item in p.get("structured_value_exemptions",[]):
        if item.get("path_suffix") and seg and seg[-1]==item["path_suffix"]: return item
        if item.get("path_segment") and item["path_segment"] in seg: return item
def validate(root:Path,policy_path:Path)->dict:
    p=yaml.safe_load(policy_path.read_text(encoding="utf-8")); rx=re.compile(p["ukrainian_character_pattern"])
    exts=set(p["scan_extensions"]); violations=[]; exemptions=[]; parse_failures=[]; scanned=0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in exts: continue
        rel=path.relative_to(root).as_posix()
        if rel.startswith(".git/"): continue
        raw=path.read_text(encoding="utf-8",errors="replace"); scanned+=1
        if not rx.search(raw): continue
        fx=_file_ex(rel,p)
        if fx:
            exemptions.append({"path":rel,"classification":fx["id"]}); continue
        if path.suffix.lower() in {".yaml",".yml",".json"}:
            try: obj=json.loads(raw) if path.suffix.lower()==".json" else yaml.safe_load(raw)
            except Exception as exc:
                expected=any(_matches(rel,g) for g in p.get("expected_invalid_yaml_globs",[])) or rel in p.get("expected_non_plain_yaml",[])
                if expected: exemptions.append({"path":rel,"classification":"expected_non_plain_or_invalid_yaml"})
                else: parse_failures.append({"path":rel,"error":str(exc)})
                continue
            for field,value in _walk(obj):
                if not rx.search(value): continue
                vx=_value_ex(field,rel,p)
                if vx: exemptions.append({"path":rel,"field_path":field,"classification":vx["id"]})
                else: violations.append({"path":rel,"field_path":field,"sample":value[:200]})
        else:
            occ=[{"line":i,"sample":line[:200]} for i,line in enumerate(raw.splitlines(),1) if rx.search(line)]
            violations.append({"path":rel,"occurrences":occ[:20]})
    status="passed" if not violations and not parse_failures else "blocked"
    return {"schema_version":"ordo.english_only_policy.report.v1","generated_at":_now(),"root":root.resolve().as_posix(),
    "policy":policy_path.resolve().as_posix(),"status":status,"scanned_files":scanned,"violation_count":len(violations),
    "parse_failure_count":len(parse_failures),"exemption_count":len(exemptions),"violations":violations,
    "parse_failures":parse_failures,"exemptions":exemptions}
def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument("root",nargs="?",type=Path,default=Path("."))
    ap.add_argument("--policy",type=Path,default=DEFAULT_POLICY); ap.add_argument("--out",type=Path); ap.add_argument("--json",action="store_true")
    a=ap.parse_args(argv); root=a.root.resolve(); pp=a.policy if a.policy.is_absolute() else (root/a.policy).resolve()
    r=validate(root,pp); payload=json.dumps(r,indent=2,ensure_ascii=False)+"\n"
    if a.out:
        op=a.out if a.out.is_absolute() else root/a.out; op.parent.mkdir(parents=True,exist_ok=True); op.write_text(payload,encoding="utf-8")
    if a.json: sys.stdout.write(payload)
    else: print(f"english-only policy: {r['status'].upper()} (violations={r['violation_count']}, parse_failures={r['parse_failure_count']}, exemptions={r['exemption_count']})")
    return 0 if r["status"]=="passed" else 1
if __name__=="__main__": raise SystemExit(main())
