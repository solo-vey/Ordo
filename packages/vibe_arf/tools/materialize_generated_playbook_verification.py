#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,shutil,subprocess,sys
from pathlib import Path
import yaml

def materialize(target: Path, vibe: Path, generate_profile: bool = True) -> dict:
    target=Path(target).resolve(); vibe=Path(vibe).resolve()
    src=target/"source/program.ordo.yaml"
    if not src.is_file():
        return {"status":"FAIL","code":"PROGRAM_SOURCE_MISSING","path":str(src)}
    program=yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    revision=str(((program.get("ordo") or {}).get("package_version") or
                  (program.get("module") or {}).get("version") or "UNKNOWN"))
    (target/"verification").mkdir(parents=True,exist_ok=True)
    (target/"tools").mkdir(parents=True,exist_ok=True)

    shutil.copy2(vibe/"PLAYBOOK_LAWS.md", target/"PLAYBOOK_LAWS.md")
    shutil.copy2(vibe/"tools/verify_execution_responsibility_map.py",
                 target/"tools/verify_execution_responsibility_map.py")
    shutil.copy2(vibe/"tools/validate_artifact_materialization_registry.py",
                 target/"tools/validate_artifact_materialization_registry.py")
    shutil.copy2(vibe/"tools/check_verification_truth.py", target/"tools/check_verification_truth.py")
    shutil.copy2(vibe/"tools/validate_authoring_information_model.py",
                 target/"tools/validate_authoring_information_model.py")
    shutil.copy2(vibe/"tools/validate_information_projection.py",
                 target/"tools/validate_information_projection.py")
    shutil.copy2(vibe/"tools/init_information_first_authoring.py",
                 target/"tools/init_information_first_authoring.py")
    # Alpha.26 analyst-minimal / simulation-first generated-playbook gates.
    alpha26_tools=[
      "_alpha26_validation_common.py",
      "validate_review_bundle_design.py","validate_proposal_canonical_separation.py","validate_approval_persistence.py",
      "validate_local_persistence_gates.py","validate_state_phase_ordering.py","validate_recovery_locality.py",
      "validate_runtime_gate_evidence.py","validate_behavioral_scenario_coverage.py","validate_semantic_dependency_inputs.py",
      "validate_simulation_evidence.py","validate_fixture_contract_closure.py","validate_defect_ownership.py",
      "validate_deterministic_contract_completeness.py","validate_artifact_archive_registry_completeness.py",
      "compile_review_bundles.py","derive_behavioral_scenario_matrix.py"
    ]
    for name in alpha26_tools:
        shutil.copy2(vibe/"tools"/name,target/"tools"/name)
    template_src=vibe/"authoring_templates/information_model"
    template_dst=target/"authoring_templates/information_model"
    template_dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(template_src,template_dst,dirs_exist_ok=True)
    # Late materialization is supported for compatibility, but Vibe should normally initialize
    # this design model before Ordo graph synthesis. Existing populated authoring files are preserved.
    init_run=subprocess.run([sys.executable,str(vibe/"tools/init_information_first_authoring.py"),str(target),
                             "--vibe-root",str(vibe)],capture_output=True,text=True,timeout=15)
    if init_run.returncode!=0:
        return {"status":"FAIL","code":"INFORMATION_FIRST_AUTHORING_INIT_FAILED",
                "stdout_tail":init_run.stdout[-1000:],"stderr_tail":init_run.stderr[-1000:]}
    # Derive low-burden review bundles and behavioral scenario families from the AIM/source.
    alpha26_authoring_files=["review_bundle_catalog.yaml","proposal_canonicalization.yaml","approval_ledger.yaml","scenario_matrix.yaml"]
    for name in alpha26_authoring_files:
        if not (target/"authoring"/name).is_file():
            return {"status":"FAIL","code":"ALPHA26_AUTHORING_FILE_MISSING","file":name}
    for tool in ["compile_review_bundles.py","derive_behavioral_scenario_matrix.py"]:
        rr=subprocess.run([sys.executable,str(vibe/"tools"/tool),str(target)],capture_output=True,text=True,timeout=15)
        if rr.returncode!=0:
            return {"status":"FAIL","code":"ALPHA26_AUTHORING_DERIVATION_FAILED","tool":tool,
                    "stdout_tail":rr.stdout[-1000:],"stderr_tail":rr.stderr[-1000:]}

    nodes=[x for x in (program.get("nodes") or []) if isinstance(x,dict) and x.get("id")]
    gates=[x for x in (program.get("gates") or []) if isinstance(x,dict) and x.get("id")]
    entries=[]
    for n in nodes:
        entries.append({"element_id":n["id"],"element_type":"node",
                        "responsibility":"","class":"UNCLASSIFIED"})
    trust_map={"deterministic":"deterministic","model_judgment":"model_judgment",
               "human":"human_authority","human_decision":"human_authority"}
    for g in gates:
        inferred=trust_map.get(str(g.get("trust_class") or ""),"UNCLASSIFIED")
        e={"element_id":g["id"],"element_type":"gate","responsibility":"","class":inferred}
        if inferred=="deterministic":
            e["mechanism"]="ordo_gate"; e["evidence_contract"]=""
        elif inferred=="model_judgment":
            e["semantic_reason"]=""; e["evidence_contract"]=""
        elif inferred=="human_authority":
            e["authority_owner"]=""; e["decision_consequence"]=""
        entries.append(e)
    rm={"schema_version":"1.0","playbook_revision":revision,"entries":entries}
    (target/"verification/EXECUTION_RESPONSIBILITY_MAP.json").write_text(
        json.dumps(rm,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    inv={"schema_version":"1.0","playbook_revision":revision,"invariants":[]}
    (target/"verification/INVARIANT_REGISTER.json").write_text(
        json.dumps(inv,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    extensions={"schema_version":"1.0","checks":[]}
    (target/"verification/PROFILE_EXTENSIONS.json").write_text(
        json.dumps(extensions,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    adapter_targets={"schema_version":"1.0","targets":["chat_internal","editor_dev"],
                     "semantic_source_of_truth":"canonical_ordo_language",
                     "note":"editor_dev is an explicit development qualification target, never language authority."}
    (target/"verification/RUNTIME_ADAPTER_TARGETS.json").write_text(
        json.dumps(adapter_targets,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    runtime_mode_contract={
      "schema_version":"1.0",
      "dry_check":{
        "must_not_fabricate_live_human_approvals":True,
        "must_not_fabricate_live_external_urls":True,
        "must_not_claim_business_ready":True,
        "allowed_terminal_semantics":"dry_check_complete_or_blocked"
      },
      "live":{
        "human_approvals_require_explicit_authority_evidence":True,
        "external_urls_require_live_specific_artifact_evidence":True
      }
    }
    (target/"verification/RUNTIME_MODE_CONTRACT.json").write_text(
        json.dumps(runtime_mode_contract,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    # Preserve a populated authoring-time registry. Do not overwrite structured artifact/archive
    # contracts with blank bootstrap placeholders during late verification materialization.
    registry_path=target/"verification/ARTIFACT_MATERIALIZATION_REGISTRY.json"
    existing_registry=None
    if registry_path.is_file():
        try:
            existing_registry=json.loads(registry_path.read_text(encoding="utf-8"))
        except Exception:
            existing_registry=None
    if isinstance(existing_registry,dict) and isinstance(existing_registry.get("artifacts"),list) and existing_registry.get("artifacts"):
        artifact_registry=existing_registry
        artifact_registry["playbook_revision"]=revision
    else:
        artifacts=[]
        nodes_by_id={str(n.get("id")):n for n in nodes}
        for o in (program.get("outputs") or []):
            if not isinstance(o,dict) or not o.get("id"):
                continue
            otype=str(o.get("type") or "").lower()
            mode="template" if otype in {"markdown","text","html","json","yaml","yml"} else "assembler"
            entry={
              "artifact_id":o["id"],
              "output_type":otype or "unknown",
              "output_path":"",
              "materialization_mode":mode,
              "content_contract":{},
              "validators":[],
              "post_materialization_validation_required":True,
              "version":"1"
            }
            # Best-effort structural bootstrap only. Required archive members/hashes and validator
            # semantics must be authored explicitly; the alpha29 completeness gate fails closed otherwise.
            matching=[]
            for n in nodes:
                art=n.get("artifact") if isinstance(n.get("artifact"),dict) else {}
                if str(art.get("artifact_id") or "")==str(o["id"]): matching.append(n)
            if len(matching)==1:
                n=matching[0]; art=n.get("artifact") if isinstance(n.get("artifact"),dict) else {}
                entry["materialization_node_id"]=n.get("id")
                entry["output_path"]=str(art.get("expected_path") or n.get("output") or "")
            if mode=="template": entry["template_path"]=""
            else: entry["assembler_ref"]=""
            artifacts.append(entry)
        artifact_registry={"schema_version":"1.0","playbook_revision":revision,"artifacts":artifacts}
    registry_path.write_text(json.dumps(artifact_registry,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    profile_ok=True; stdout_tail=""; stderr_tail=""
    if generate_profile:
        p=subprocess.run([sys.executable,str(vibe/"tools/generate_verification_profile.py"),str(target)],
                         capture_output=True,text=True,timeout=15)
        profile_ok=p.returncode==0
        stdout_tail=p.stdout[-1000:]; stderr_tail=p.stderr[-1000:]
    return {
      "status":"PASS" if profile_ok else "FAIL",
      "package":str(target),"playbook_revision":revision,
      "responsibility_entries":len(entries),
      "verification_profile_generated":profile_ok if generate_profile else False,
      "profile_generation_skipped":not generate_profile,
      "generator_stdout_tail":stdout_tail,
      "generator_stderr_tail":stderr_tail,
      "note":"Responsibility map is intentionally UNCLASSIFIED/incomplete until Vibe completes mechanization design."
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--vibe-root",default=str(Path(__file__).resolve().parents[1]))
    a=ap.parse_args()
    result=materialize(Path(a.package),Path(a.vibe_root))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result.get("status")=="PASS" else 1

if __name__=="__main__": raise SystemExit(main())
