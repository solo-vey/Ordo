#!/usr/bin/env python3
import argparse, json, sys
DIMS = [
    "scope_locality", "ownership_clarity", "shared_contract_impact", "blast_radius",
    "cross_module_dependency", "backward_compatibility", "migration_operational_impact", "verification_confidence"
]
SCORE = {"LOW": 0, "MEDIUM": 1, "HIGH": 3}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assessment-json", required=True)
    args = ap.parse_args()
    raw = json.load(open(args.assessment_json, encoding="utf-8"))
    levels, errors = {}, []
    for dim in DIMS:
        value = raw.get(dim)
        level = str(value.get("level", "") if isinstance(value, dict) else (value or "")).upper()
        if level not in SCORE:
            errors.append(f"{dim}: expected LOW/MEDIUM/HIGH, got {value!r}")
        else:
            levels[dim] = level
    if errors:
        print(json.dumps({"status": "INVALID", "errors": errors}, ensure_ascii=False, indent=2))
        return 2
    total = sum(SCORE[levels[d]] for d in DIMS)
    if any(levels[d] == "HIGH" for d in DIMS) or total >= 5:
        overall = "HIGH"
    elif any(levels[d] == "MEDIUM" for d in DIMS):
        overall = "MEDIUM"
    else:
        overall = "LOW"
    decision = "HANDOFF_REQUIRED" if overall == "HIGH" else "LOCAL_SAFE"
    drivers = [d for d in DIMS if levels[d] == "HIGH"] or ([d for d in DIMS if levels[d] == "MEDIUM"] if overall == "MEDIUM" else [])
    print(json.dumps({
        "status": "OK", "dimensions": levels, "total_score": total,
        "overall_risk": overall, "implementation_decision": decision, "risk_drivers": drivers
    }, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
