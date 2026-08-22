#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,yaml,tempfile,shutil,importlib.util
R=Path(__file__).resolve().parents[1]
checks={}

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

program=yaml.safe_load((R/"source/program.ordo.yaml").read_text(encoding="utf-8")) or {}
nodes={x["id"]:x for x in program.get("nodes",[]) if isinstance(x,dict) and x.get("id")}
gates={x["id"]:x for x in program.get("gates",[]) if isinstance(x,dict) and x.get("id")}
expected={
 "G_UNDERSTANDING_READY","G_PARAMETER_FLOW_READY","G_LANGUAGE_GROUNDING_READY",
 "G_VERIFICATION_READY","G_REVIEW_EXPERIENCE_READY","G_PACKAGE_READY",
 "G_DELIVERY_READY","G_FINAL_DIALOGUE_READY","G_USER_ACCEPTANCE_CONFIRMED"
}
checks["core_staged_quality_boundaries_present"]=expected.issubset(set(gates))
# Additional RUN->GATE boundaries are allowed when they represent distinct control semantics.
checks["no_return_to_monolithic_final_gate_wall"]=all(
    g in gates for g in ["G_SOURCE_VERIFICATION_PASS","G_STRUCTURE_VERIFICATION_PASS",
                         "G_ARTIFACT_VERIFICATION_PASS","G_REGRESSION_VERIFICATION_PASS",
                         "G_RELEASE_VERIFICATION_PASS"]
)

# Boundaries immediately follow their evidence-producing stages.
pairs={
 "N_U_CHAT_FIRST_BOOTSTRAP_CHECK":"G_UNDERSTANDING_READY",
 "N_P_ANSWER_PROPAGATION":"G_PARAMETER_FLOW_READY",
 "N_B_ORDO_LANGUAGE_GROUNDING_CHECK":"G_LANGUAGE_GROUNDING_READY",
 "N_R_VERIFICATION_READINESS":"G_VERIFICATION_READY",
 "N_PK_FINAL_EXPERIENCE_EVIDENCE":"G_DELIVERY_READY"
}
def outgoing(n):
    oa=n.get("on_answer")
    if isinstance(oa,dict) and isinstance(oa.get("next"),str): return oa["next"]
    return n.get("next")
checks["boundaries_near_evidence_producers"]=all(outgoing(nodes[n])==g for n,g in pairs.items())
checks["package_boundary_preserves_continuity_run_gate"]= (
    outgoing(nodes["N_PI_GENERATED_PLAYBOOK_PACKAGE_RECORD_DELIVERY_EVIDENCE"])=="N_PK_PACKAGE_CONTINUITY_AUDIT"
    and outgoing(nodes["N_PK_PACKAGE_CONTINUITY_AUDIT"])=="G_PK_PACKAGE_CONTINUITY_VALID"
    and gates["G_PK_PACKAGE_CONTINUITY_VALID"].get("on_pass")=="G_PACKAGE_READY"
)

# Output exposure is lifecycle-specific, not the old all-gates list.
outs={o["id"]:o for o in program.get("outputs",[]) if isinstance(o,dict) and o.get("id")}
checks["business_view_output_at_presentation"]=outs.get("OUT_BUSINESS_VIEW",{}).get("allowed_after") in (["N_PRESENT_BUSINESS_VIEW"],["N_OUT_BUSINESS_VIEW_MATERIALIZE"],["N_PI_BUSINESS_VIEW_DOCUMENT_REGISTER_ARTIFACT"])
checks["package_output_after_final_acceptance"]=outs.get("OUT_GENERATED_PLAYBOOK_PACKAGE",{}).get("allowed_after") in (["G_USER_ACCEPTANCE_CONFIRMED"],["N_OUT_GENERATED_PACKAGE_HANDOFF"])

# Current materialization registry is complete.
validator=load("a14_artifacts",R/"tools/validate_artifact_materialization_registry.py")
vr=validator.validate_package(R)
checks["self_artifact_materialization_registry_passes"]=vr.get("status")=="PASS"

# Mandatory profile contract includes materialization registry.
registry=json.loads((R/"source/verification-runner-registry.json").read_text(encoding="utf-8"))
pre=set((registry.get("mandatory_profile_contract") or {}).get("PRE_EDITOR") or [])
checks["materialization_runner_mandatory"]="artifact_materialization_registry" in pre

# Generated-playbook materializer creates a fail-closed artifact scaffold.
mat=load("a14_mat",R/"tools/materialize_generated_playbook_verification.py")
with tempfile.TemporaryDirectory() as td:
    target=Path(td)/"sample"; target.mkdir()
    shutil.copytree(R/"source",target/"source")
    result=mat.materialize(target,R,generate_profile=False)
    checks["materializer_runs"]=result.get("status")=="PASS"
    checks["materializer_installs_artifact_validator"]=(target/"tools/validate_artifact_materialization_registry.py").is_file()
    checks["materializer_creates_artifact_registry"]=(target/"verification/ARTIFACT_MATERIALIZATION_REGISTRY.json").is_file()
    fixture_result=validator.validate_package(target)
    checks["generated_scaffold_fails_closed_until_templates_bound"]=fixture_result.get("status")=="FAIL"

status="PASS" if all(checks.values()) else "FAIL"
print(json.dumps({"status":status,"checks":checks},ensure_ascii=False,indent=2))
raise SystemExit(0 if status=="PASS" else 1)
