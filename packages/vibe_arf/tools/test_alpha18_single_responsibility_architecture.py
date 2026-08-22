#!/usr/bin/env python3
from pathlib import Path
import json,yaml
R=Path(__file__).resolve().parents[1]
d=yaml.safe_load((R/"source/program.ordo.yaml").read_text(encoding="utf-8")) or {}
nodes={n["id"]:n for n in d.get("nodes",[]) if isinstance(n,dict) and n.get("id")}
gates={g["id"]:g for g in d.get("gates",[]) if isinstance(g,dict) and g.get("id")}
checks={}

checks["obsolete_multi_responsibility_nodes_removed"]=all(x not in nodes for x in [
    "N_B_SOURCE_COMPILE_VALIDATION","N_R_READINESS"
])

# Five verification nodes only execute/record; gates decide.
pairs=[
 ("N_VERIFY_SOURCE","G_SOURCE_VERIFICATION_PASS","N_VERIFY_INFORMATION_PROJECTION"),
 ("N_VERIFY_INFORMATION_PROJECTION","G_INFORMATION_PROJECTION_PASS","N_VERIFY_STRUCTURE"),
 ("N_VERIFY_STRUCTURE","G_STRUCTURE_VERIFICATION_PASS","N_VERIFY_ARTIFACTS"),
 ("N_VERIFY_ARTIFACTS","G_ARTIFACT_VERIFICATION_PASS","N_VERIFY_REGRESSION"),
 ("N_VERIFY_REGRESSION","G_REGRESSION_VERIFICATION_PASS","N_VERIFY_RELEASE"),
 ("N_VERIFY_RELEASE","G_RELEASE_VERIFICATION_PASS","N_B_ORDO_LANGUAGE_GROUNDING_CHECK"),
]
def nxt(nid):
    oa=nodes[nid].get("on_answer") or {}
    return oa.get("next") if isinstance(oa,dict) else nodes[nid].get("next")
checks["verification_is_run_then_gate"]=all(
    nxt(n)==g and gates.get(g,{}).get("on_pass")==dest and gates.get(g,{}).get("trust_class")=="deterministic"
    for n,g,dest in pairs
)

# Review quality responsibilities separated.
checks["review_readiness_split"]=(
    nxt("N_R_VERIFICATION_READINESS")=="G_VERIFICATION_READY"
    and gates["G_VERIFICATION_READY"].get("on_pass") in {"N_R_AUTHORING_BURDEN","N_SIM_INSPECT"}
    and (gates["G_VERIFICATION_READY"].get("on_pass")!="N_SIM_INSPECT" or (
        nxt("N_SIM_INSPECT")=="N_SIM_FIXTURE_SYNTHESIS"
        and nxt("N_SIM_FIXTURE_SYNTHESIS")=="N_SIM_RUN"
        and nxt("N_SIM_RUN")=="N_SIM_CLASSIFY"
    ))
    and nxt("N_R_AUTHORING_BURDEN")=="N_R_ANALYST_EXPERIENCE"
    and nxt("N_R_ANALYST_EXPERIENCE")=="G_REVIEW_EXPERIENCE_READY"
)

# Business output materialize != validate != present.
checks["business_view_materialize_validate_present_split"]=(
    nxt("N_PI_BUSINESS_VIEW_DOCUMENT_MATERIALIZE")=="N_PI_BUSINESS_VIEW_DOCUMENT_RENDERED_ARTIFACT_VALIDATE"
    and nxt("N_PI_BUSINESS_VIEW_DOCUMENT_RENDERED_ARTIFACT_VALIDATE")=="G_PI_BUSINESS_VIEW_DOCUMENT_RENDERED_ARTIFACT_GATE"
    and gates["G_PI_BUSINESS_VIEW_DOCUMENT_RENDERED_ARTIFACT_GATE"].get("on_pass")=="N_PI_BUSINESS_VIEW_DOCUMENT_REGISTER_ARTIFACT"
    and nxt("N_PI_BUSINESS_VIEW_DOCUMENT_REGISTER_ARTIFACT")=="N_PRESENT_BUSINESS_VIEW"
)

# Delivery responsibilities separated and no synthetic hardcoded PASS.
checks["delivery_integrity_human_format_split"]=(
    nxt("N_PK_DELIVERY_VALIDATE")=="N_PK_HUMAN_FORMAT_VALIDATE"
    and nxt("N_PK_HUMAN_FORMAT_VALIDATE")=="N_PK_DELIVERY_EVIDENCE"
)
checks["delivery_evidence_continuity_experience_split"]=(
    nxt("N_PK_DELIVERY_EVIDENCE")=="N_PK_CONTINUITY_EVIDENCE"
    and nxt("N_PK_CONTINUITY_EVIDENCE")=="N_PK_FINAL_EXPERIENCE_EVIDENCE"
    and nxt("N_PK_FINAL_EXPERIENCE_EVIDENCE")=="G_DELIVERY_READY"
)
final_updates=((nodes["N_PK_FINAL_EXPERIENCE_EVIDENCE"].get("on_answer") or {}).get("update_state") or {})
checks["final_experience_pass_not_hardcoded"]=all(
    str(final_updates.get(k,"")).startswith("$answer.")
    for k in ["autonomous_until_blocker_status","first_question_quality_status","e2e_authoring_trial_status"]
)

# Generated package output materialize != validate != handoff.
checks["generated_package_materialize_validate_handoff_split"]=(
    gates["G_USER_ACCEPTANCE_CONFIRMED"].get("on_pass")=="N_OUT_GENERATED_PACKAGE_MATERIALIZE"
    and nxt("N_OUT_GENERATED_PACKAGE_MATERIALIZE")=="G_GENERATED_PACKAGE_OUTPUT_VALID"
    and gates["G_GENERATED_PACKAGE_OUTPUT_VALID"].get("on_pass")=="N_OUT_GENERATED_PACKAGE_HANDOFF"
    and nxt("N_OUT_GENERATED_PACKAGE_HANDOFF")=="END_PLAYBOOK_PACKAGE_ACCEPTED"
)

# Current graph itself is the audit surface. Historical pre/post repair report files are not release inputs.
checks["current_graph_ids_unique"]=(len(nodes)==len(set(nodes)) and len(gates)==len(set(gates)))
checks["pattern_realization_run_gate_split"]=(
    nxt("N_VERIFY_PATTERN_GRAPH_REALIZATION")=="G_PATTERN_GRAPH_REALIZATION_VALID"
    and gates["G_PATTERN_GRAPH_REALIZATION_VALID"].get("on_pass")=="N_VERIFY_SOURCE"
    and gates["G_PATTERN_GRAPH_REALIZATION_VALID"].get("trust_class")=="deterministic"
)
checks["package_readiness_run_gate_split"]=(
    nxt("N_PI_GENERATED_PLAYBOOK_PACKAGE_PACKAGE_READINESS_CHECK")=="G_PI_GENERATED_PLAYBOOK_PACKAGE_PACKAGE_READINESS_GATE"
    and gates["G_PI_GENERATED_PLAYBOOK_PACKAGE_PACKAGE_READINESS_GATE"].get("on_pass")=="N_PI_GENERATED_PLAYBOOK_PACKAGE_DEPENDENCY_CLOSURE"
)

laws_text=(R/"PLAYBOOK_LAWS.md").read_text(encoding="utf-8")
checks["single_responsibility_is_governing_law"]="E6_SINGLE_RESPONSIBILITY_EXECUTION" in laws_text

status="PASS" if all(checks.values()) else "FAIL"
print(json.dumps({"status":status,"checks":checks},ensure_ascii=False,indent=2))
raise SystemExit(0 if status=="PASS" else 1)
