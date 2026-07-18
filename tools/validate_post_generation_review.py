#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, sys

GATES = [
"EVIDENCE-COVERAGE-01","NO-UNSUPPORTED-INFERENCE-01","CANONICAL-CONTRACT-01",
"CURRENT-VERSION-RECONCILIATION-01","PATH-DOMAIN-01","ROLLBACK-CONTRACT-01",
"CROSS-ARTIFACT-01","ADVERSARIAL-REVIEW-01","POST-CORRECTION-REVIEW-01"
]
ALLOWED_SOURCE = {"confirmed_user","canonical_example","repository_derived","package_confirmed","official_schema"}
NON_MATERIAL = {"model_proposed","unknown"}

def validate(root, record):
    errors=[]
    required=["schema_version","review_id","artifact","criticality","review_profile","authoritative_sources",
              "claims","defects","invalidated_sections","preserved_sections","corrections",
              "cross_artifact_checks","regression_checks","gates","confirmation_eligibility","trace_events"]
    for k in required:
        if k not in record: errors.append(f"missing field: {k}")
    if errors: return errors
    if record["schema_version"]!="ordo.apf.post_generation_review_record.v1":
        errors.append("unsupported schema_version")
    art=record["artifact"]
    p=root/art["path"]
    if not p.exists(): errors.append("reviewed artifact missing")
    else:
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != art["sha256"]: errors.append("reviewed artifact sha256 mismatch")
    source_ids={s["source_id"] for s in record["authoritative_sources"] if s.get("status")=="verified"}
    for s in record["authoritative_sources"]:
        if s.get("source_class") not in ALLOWED_SOURCE: errors.append(f"invalid source class: {s.get('source_id')}")
        locator=root/s.get("locator","")
        if s.get("status")=="verified":
            if not locator.exists(): errors.append(f"source missing: {s.get('source_id')}")
            elif hashlib.sha256(locator.read_bytes()).hexdigest()!=s.get("sha256"): errors.append(f"source sha mismatch: {s.get('source_id')}")
    for c in record["claims"]:
        sensitivity=c.get("sensitivity")
        cls=c.get("materialization_class")
        status=c.get("status")
        refs=set(c.get("source_ids",[]))
        if sensitivity in {"executable","contract-sensitive"} and status=="supported":
            if cls in NON_MATERIAL: errors.append(f"unsupported materialized claim: {c.get('claim_id')}")
            if not refs or not refs.issubset(source_ids): errors.append(f"unverified claim source: {c.get('claim_id')}")
    open_blocking=[d for d in record["defects"] if d.get("severity") in {"critical","high"} and d.get("status")=="open"]
    if open_blocking and record["confirmation_eligibility"].get("eligible"):
        errors.append("eligible with open critical/high defects")
    for g in GATES:
        if record["gates"].get(g) not in {"passed","failed","not-applicable"}:
            errors.append(f"invalid or missing gate: {g}")
    required_gate_fail=[g for g in GATES if record["gates"].get(g)=="failed"]
    if record["confirmation_eligibility"].get("eligible") and required_gate_fail:
        errors.append("eligible with failed gates")
    if record["criticality"]=="critical" and record["review_profile"]!="full":
        errors.append("critical artifact without full profile")
    material_corrections=[c for c in record["corrections"] if c.get("status")=="completed"]
    if material_corrections:
        if record["gates"].get("POST-CORRECTION-REVIEW-01")!="passed":
            errors.append("completed correction without passed post-correction review")
        if not all(c.get("validator_independent") for c in material_corrections):
            errors.append("correction self-attestation detected")
    return errors

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("record")
    ap.add_argument("--root",default=".")
    a=ap.parse_args()
    root=Path(a.root).resolve()
    rec=json.loads(Path(a.record).read_text(encoding="utf-8"))
    errors=validate(root,rec)
    print(json.dumps({"status":"PASS" if not errors else "FAIL","errors":errors},indent=2))
    return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
