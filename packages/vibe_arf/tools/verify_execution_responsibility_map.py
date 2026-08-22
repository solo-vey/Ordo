#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import yaml

CLASSES={"deterministic","model_judgment","human_authority"}
MECHANISMS={"ordo_gate","ordo_state_transition","cli_helper","package_local_python"}

def validate_package(root: Path, map_rel: str="verification/EXECUTION_RESPONSIBILITY_MAP.json") -> dict:
    root=Path(root).resolve()
    src=root/"source/program.ordo.yaml"; mp=root/map_rel
    findings=[]
    if not src.is_file(): findings.append({"code":"PROGRAM_SOURCE_MISSING","path":str(src)})
    if not mp.is_file(): findings.append({"code":"RESPONSIBILITY_MAP_MISSING","path":str(mp)})
    if findings:
        return {"status":"FAIL","source":str(src),"map":str(mp),"elements_total":0,"entries_total":0,"findings":findings}
    program=yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    data=json.loads(mp.read_text(encoding="utf-8"))
    nodes={x.get("id"):x for x in (program.get("nodes") or []) if isinstance(x,dict) and x.get("id")}
    gates={x.get("id"):x for x in (program.get("gates") or []) if isinstance(x,dict) and x.get("id")}
    expected={**{k:"node" for k in nodes},**{k:"gate" for k in gates}}
    entries=data.get("entries"); entries=entries if isinstance(entries,list) else []
    by_id={}
    for i,e in enumerate(entries):
        if not isinstance(e,dict):
            findings.append({"code":"ENTRY_NOT_OBJECT","index":i}); continue
        eid=e.get("element_id")
        if not eid:
            findings.append({"code":"ELEMENT_ID_REQUIRED","index":i}); continue
        if eid in by_id: findings.append({"code":"DUPLICATE_ELEMENT_ENTRY","element_id":eid})
        by_id[eid]=e
        if eid not in expected:
            findings.append({"code":"UNKNOWN_ELEMENT","element_id":eid}); continue
        if e.get("element_type")!=expected[eid]:
            findings.append({"code":"ELEMENT_TYPE_MISMATCH","element_id":eid,
                             "expected":expected[eid],"actual":e.get("element_type")})
        cls=e.get("class")
        if cls not in CLASSES:
            findings.append({"code":"INVALID_CLASS","element_id":eid,"class":cls}); continue
        if not str(e.get("responsibility") or "").strip():
            findings.append({"code":"RESPONSIBILITY_REQUIRED","element_id":eid})
        if cls=="deterministic":
            mech=e.get("mechanism")
            if mech not in MECHANISMS:
                findings.append({"code":"DETERMINISTIC_MECHANISM_REQUIRED","element_id":eid,"mechanism":mech})
            if not str(e.get("evidence_contract") or "").strip():
                findings.append({"code":"DETERMINISTIC_EVIDENCE_REQUIRED","element_id":eid})
            if mech in {"cli_helper","package_local_python"} and not (e.get("tool_or_validator_refs") or []):
                findings.append({"code":"DETERMINISTIC_TOOL_REF_REQUIRED","element_id":eid})
            if mech=="package_local_python":
                for ref in e.get("tool_or_validator_refs") or []:
                    p=(root/str(ref)).resolve()
                    try: p.relative_to(root)
                    except Exception:
                        findings.append({"code":"PYTHON_TOOL_OUTSIDE_PACKAGE","element_id":eid,"ref":ref}); continue
                    if not p.is_file(): findings.append({"code":"PYTHON_TOOL_MISSING","element_id":eid,"ref":ref})
        elif cls=="model_judgment":
            if not str(e.get("semantic_reason") or "").strip():
                findings.append({"code":"MODEL_JUDGMENT_SEMANTIC_REASON_REQUIRED","element_id":eid})
            if not str(e.get("evidence_contract") or "").strip():
                findings.append({"code":"MODEL_JUDGMENT_EVIDENCE_REQUIRED","element_id":eid})
        elif cls=="human_authority":
            if not str(e.get("authority_owner") or "").strip():
                findings.append({"code":"HUMAN_AUTHORITY_OWNER_REQUIRED","element_id":eid})
            if not str(e.get("decision_consequence") or "").strip():
                findings.append({"code":"HUMAN_DECISION_CONSEQUENCE_REQUIRED","element_id":eid})
    for eid,etype in expected.items():
        if eid not in by_id:
            findings.append({"code":"EXECUTABLE_ELEMENT_UNCLASSIFIED","element_id":eid,"element_type":etype})
    for gid,g in gates.items():
        e=by_id.get(gid) or {}; tc=str(g.get("trust_class") or "").strip()
        expected_class={"deterministic":"deterministic","model_judgment":"model_judgment",
                        "human":"human_authority","human_decision":"human_authority"}.get(tc)
        if expected_class and e.get("class") not in {None,expected_class}:
            findings.append({"code":"GATE_TRUST_CLASS_CONFLICT","element_id":gid,
                             "source_trust_class":tc,"map_class":e.get("class")})
    return {"status":"PASS" if not findings else "FAIL","source":str(src),"map":str(mp),
            "elements_total":len(expected),"entries_total":len(entries),"findings":findings}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("package",nargs="?",default=".")
    ap.add_argument("--map",default="verification/EXECUTION_RESPONSIBILITY_MAP.json")
    a=ap.parse_args()
    result=validate_package(Path(a.package),a.map)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["status"]=="PASS" else 1

if __name__=="__main__": raise SystemExit(main())
