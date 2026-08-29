from __future__ import annotations
import json
from pathlib import Path

ALLOWED_STATUS={"candidate","validated","stable","deprecated"}

def load_registry(path: str|Path)->dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate_registry(data:dict)->list[dict]:
    issues=[]; seen=set(); pats=data.get("patterns",[])
    for p in pats:
        pid=p.get("id")
        if not isinstance(pid,str) or not pid.startswith("PAT-"): issues.append({"code":"PATTERN_ID_INVALID","pattern":pid})
        if pid in seen: issues.append({"code":"PATTERN_ID_DUPLICATE","pattern":pid})
        seen.add(pid)
        if p.get("status") not in ALLOWED_STATUS: issues.append({"code":"PATTERN_STATUS_INVALID","pattern":pid})
        if len(p.get("steps",[]))<2: issues.append({"code":"PATTERN_STEPS_INSUFFICIENT","pattern":pid})
        if not p.get("evidence_requirements"): issues.append({"code":"PATTERN_EVIDENCE_MISSING","pattern":pid})
        packages=p.get("provenance",{}).get("packages",[])
        if p.get("status")=="stable" and len(set(packages))<2: issues.append({"code":"PATTERN_STABLE_EVIDENCE_INSUFFICIENT","pattern":pid})
        if not p.get("review_template",{}).get("decision_values"): issues.append({"code":"PATTERN_REVIEW_DECISIONS_MISSING","pattern":pid})
    return issues

def recommend(data:dict, capabilities:set[str])->list[str]:
    out=[]
    for p in data.get("patterns",[]):
        req=set(p.get("applicability",{}).get("requires",[])); exc=set(p.get("applicability",{}).get("excludes",[]))
        if p.get("status") in {"validated","stable"} and req<=capabilities and not (exc & capabilities): out.append(p["id"])
    return sorted(out)

def compose(data:dict, pattern_ids:list[str])->dict:
    by={p["id"]:p for p in data.get("patterns",[])}
    missing=[x for x in pattern_ids if x not in by]
    if missing: return {"status":"failed","issues":[{"code":"PATTERN_UNKNOWN","patterns":missing}]}
    for a,b in zip(pattern_ids,pattern_ids[1:]):
        allowed=set(by[a].get("composition",{}).get("may_precede",[]))|set(by[b].get("composition",{}).get("may_follow",[]))
        if b not in allowed and a not in allowed:
            return {"status":"failed","issues":[{"code":"PATTERN_COMPOSITION_NOT_DECLARED","from":a,"to":b}]}
    return {"status":"passed","sequence":pattern_ids}

def render_review_card(pattern:dict, evidence:dict)->dict:
    missing=[x for x in pattern["evidence_requirements"] if x not in evidence]
    return {"pattern_id":pattern["id"],"sections":pattern["review_template"]["sections"],"evidence":evidence,"missing_evidence":missing,"decision":"blocked" if missing else "pending_human_review","allowed_decisions":pattern["review_template"]["decision_values"]}
