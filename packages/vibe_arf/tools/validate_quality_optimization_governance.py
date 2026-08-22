#!/usr/bin/env python3
from pathlib import Path
import json,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1]).resolve()
p=root/'source/quality-optimization-governance-policy.json'
errs=[]
try: d=json.loads(p.read_text())
except Exception as e: print(json.dumps({"status":"FAIL","errors":["POLICY_READ:"+str(e)]},indent=2)); raise SystemExit(1)
for x in ["correctness","safety_authority","efficiency","artifact_quality"]:
    if x not in d.get("acceptance_dimensions",{}): errs.append("MISSING_DIMENSION:"+x)
cal=d.get("calibration",{})
if cal.get("hard_law_compliance_reward")!=0: errs.append("HARD_LAW_REWARD_NONZERO")
if cal.get("uncalibrated_diagnostic_score_effect")!=0: errs.append("UNCALIBRATED_DIAGNOSTIC_NONZERO")
acc=d.get("optimization_acceptance",{})
for x in ["reject_if_any_protected_quality_dimension_regresses","end_to_end_improvement_required","local_metric_gain_alone_is_insufficient"]:
    if acc.get(x) is not True: errs.append("ACCEPTANCE_RULE_MISSING:"+x)
h=d.get("optimization_history",{})
for x in ["problem","baseline_evidence","hypothesis","protected_invariants","regression_asset","change","comparison_evidence","measured_result","limitations","decision"]:
    if x not in h.get("required_fields",[]): errs.append("HISTORY_FIELD_MISSING:"+x)
print(json.dumps({"status":"PASS" if not errs else "FAIL","errors":errs,"policy_id":d.get("policy_id")},indent=2))
raise SystemExit(0 if not errs else 1)
