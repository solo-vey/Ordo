#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import yaml

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--output",default="verification_profile.json")
    a=ap.parse_args()
    root=Path(a.package).resolve()
    src=root/"source/program.ordo.yaml"
    if not src.is_file():
        print(json.dumps({"status":"FAIL","code":"PROGRAM_SOURCE_MISSING","path":str(src)},indent=2)); return 2
    d=yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    revision=str(((d.get("ordo") or {}).get("package_version")
                  or (d.get("module") or {}).get("version") or "UNKNOWN"))
    pkgid=str(((d.get("ordo") or {}).get("package") or (d.get("module") or {}).get("id") or root.name))
    checks=[
      {"id":"lint","runner":"ordo_lint","phase":"FAST","required":True,"timeout_seconds":60,
       "invariants":["LANGUAGE_SOURCE_VALID"]},
      {"id":"compile","runner":"ordo_compile","phase":"FAST","required":True,"timeout_seconds":90,
       "depends_on":["lint"],"invariants":["IR_COMPILABLE"]},
      {"id":"tests","runner":"ordo_test","phase":"PRE_EDITOR","required":True,"timeout_seconds":120,
       "depends_on":["compile"],"invariants":["DECLARED_REGRESSIONS_PASS"]},
      {"id":"coverage","runner":"ordo_coverage","phase":"PRE_EDITOR","required":True,"timeout_seconds":90,
       "depends_on":["tests"],"invariants":["COVERAGE_REPORTED_TRUTHFULLY"]},
      {"id":"runtime","runner":"ordo_runtime_status","phase":"PRE_EDITOR","required":True,"timeout_seconds":60,
       "depends_on":["compile"],"invariants":["RUNTIME_PLAN_CURRENT"]},
      {"id":"targets","runner":"ordo_verify_targets","phase":"PRE_EDITOR","required":True,"timeout_seconds":60,
       "depends_on":["compile"],"invariants":["TARGETS_INTEGRITY"]},
      {"id":"laws","runner":"laws_verbatim","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "invariants":["GOVERNING_LAWS_PROPAGATED"]},
      {"id":"source_uniqueness","runner":"delivery_source_uniqueness","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "invariants":["SINGLE_EXECUTABLE_SOURCE"]},
      {"id":"editor_graph","runner":"editor_runtime_graph","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "depends_on":["compile"],"invariants":["EDITOR_RUNTIME_GRAPH_COMPATIBLE"]},
      {"id":"generated_playbook_language_core","runner":"generated_playbook_contract","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"target":"language_core"},"depends_on":["compile"],"invariants":["ORDO_LANGUAGE_CONFORMANCE"]},
      {"id":"deterministic_contract_completeness","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_deterministic_contract_completeness.py","argv":["{package_root}"]},
       "depends_on":["generated_playbook_language_core"],"invariants":["DETERMINISTIC_CONTRACT_COMPLETE"]},
      {"id":"artifact_archive_registry_completeness","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_artifact_archive_registry_completeness.py","argv":["{package_root}"]},
       "depends_on":["deterministic_contract_completeness"],"invariants":["ARTIFACT_ARCHIVE_REGISTRY_COMPLETE"]},
      {"id":"authoring_information_model","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_authoring_information_model.py","argv":["{package_root}"]},
       "depends_on":["compile"],"invariants":["AUTHORING_INFORMATION_MODEL_VALID"]},
      {"id":"information_projection","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_information_projection.py","argv":["{package_root}","--playbook","{package_root}/source/program.ordo.yaml","--require-bound"]},
       "depends_on":["authoring_information_model","generated_playbook_language_core"],
       "invariants":["INFORMATION_MODEL_ORDO_BIDIRECTIONAL_TRACEABILITY"]},
      {"id":"review_bundle_design","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_review_bundle_design.py","argv":["{package_root}"]},"depends_on":["authoring_information_model"],"invariants":["ANALYST_MINIMAL_REVIEW_BUNDLES"]},
      {"id":"proposal_canonical_separation","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_proposal_canonical_separation.py","argv":["{package_root}"]},"depends_on":["authoring_information_model"],"invariants":["PROPOSAL_IS_NOT_CANONICAL_TRUTH"]},
      {"id":"approval_persistence","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_approval_persistence.py","argv":["{package_root}"]},"depends_on":["review_bundle_design"],"invariants":["APPROVAL_LEDGER_PRESERVES_PRIOR_AUTHORITY"]},
      {"id":"local_persistence_gates","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_local_persistence_gates.py","argv":["{package_root}"]},"depends_on":["approval_persistence"],"invariants":["HUMAN_AUTHORITY_PERSISTENCE_VERIFIED_LOCALLY"]},
      {"id":"state_phase_ordering","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_state_phase_ordering.py","argv":["{package_root}"]},"depends_on":["generated_playbook_language_core"],"invariants":["GATE_POSTCONDITION_ORDERING"]},
      {"id":"recovery_locality","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_recovery_locality.py","argv":["{package_root}"]},"depends_on":["information_projection"],"invariants":["RECOVERY_RETURNS_TO_NEAREST_CAUSAL_REMEDIATION"]},
      {"id":"semantic_dependency_inputs","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_semantic_dependency_inputs.py","argv":["{package_root}"]},"depends_on":["generated_playbook_language_core"],"invariants":["AUTHORITY_SOURCES_DECLARED_AS_INPUTS"]},
      {"id":"generated_playbook_vibe_profile","runner":"generated_playbook_contract","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"target":"vibe_authoring"},"depends_on":["generated_playbook_language_core","information_projection"],"invariants":["VIBE_AUTHORING_PROFILE_CONFORMANCE"]},
      {"id":"generated_playbook_auto_answers","runner":"generated_playbook_contract","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"target":"auto_answers"},"depends_on":["generated_playbook_language_core"],"invariants":["AUTO_ANSWERS_TEST_SCENARIO_CONFORMANCE"]},
      {"id":"behavioral_scenario_coverage","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_behavioral_scenario_coverage.py","argv":["{package_root}"]},"depends_on":["generated_playbook_auto_answers"],"invariants":["BEHAVIORAL_COVERAGE_DERIVED_FROM_SCENARIO_MATRIX"]},
      {"id":"simulation_evidence","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_simulation_evidence.py","argv":["{package_root}"]},"depends_on":["behavioral_scenario_coverage","artifact_archive_registry_completeness"],"invariants":["PINNED_RUNTIME_SIMULATION_PASS"]},
      {"id":"fixture_contract_closure","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_fixture_contract_closure.py","argv":["{package_root}"]},"depends_on":["simulation_evidence"],"invariants":["SIMULATION_FIXTURE_CONTRACT_CLOSED"]},
      {"id":"runtime_gate_evidence","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_runtime_gate_evidence.py","argv":["{package_root}"]},"depends_on":["simulation_evidence"],"invariants":["RUNTIME_GATE_EVIDENCE_NON_VACUOUS"]},
      {"id":"defect_ownership","runner":"python_script","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"script":"tools/validate_defect_ownership.py","argv":["{package_root}"]},"depends_on":["simulation_evidence"],"invariants":["FAILURES_CLASSIFIED_WITHOUT_WORKAROUND_POLLUTION"]},
      {"id":"generated_playbook_editor_adapter","runner":"generated_playbook_contract","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "args":{"target":"editor_dev"},"depends_on":["generated_playbook_vibe_profile","generated_playbook_auto_answers","fixture_contract_closure","runtime_gate_evidence","defect_ownership"],"invariants":["ORDO_VALID_EDITOR_ADAPTER_COMPATIBLE"]},
      {"id":"execution_responsibility_map","runner":"execution_responsibility_map","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "depends_on":["compile"],"invariants":["MODEL_ONLY_WHERE_DETERMINISM_ENDS","EXECUTION_RESPONSIBILITIES_CLASSIFIED"]},
      {"id":"artifact_materialization_registry","runner":"artifact_materialization_registry","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "depends_on":["compile"],"invariants":["EVERY_DECLARED_OUTPUT_HAS_EXPLICIT_MATERIALIZATION_CONTRACT"]},
      {"id":"language_validate_artifacts","runner":"ordo_validate_artifacts","phase":"PRE_EDITOR","required":True,"timeout_seconds":60,
       "depends_on":["compile"],"invariants":["LANGUAGE_RENDERED_ARTIFACT_VALIDATION"]},
      {"id":"language_consistency","runner":"ordo_consistency","phase":"PRE_EDITOR","required":True,"timeout_seconds":60,
       "depends_on":["language_validate_artifacts"],"invariants":["LANGUAGE_CROSS_ARTIFACT_CONSISTENCY"]},
      {"id":"language_validate_output","runner":"ordo_validate_output","phase":"PRE_EDITOR","required":True,"timeout_seconds":60,
       "depends_on":["compile"],"invariants":["LANGUAGE_OUTPUT_VALIDATION"]},
      {"id":"language_validate_lock","runner":"ordo_validate_lock","phase":"PRE_EDITOR","required":True,"timeout_seconds":60,
       "depends_on":["compile"],"invariants":["LANGUAGE_DEPENDENCY_LOCK_VALID"]},
      {"id":"language_check_conflicts","runner":"ordo_check_conflicts","phase":"PRE_EDITOR","required":True,"timeout_seconds":60,
       "depends_on":["language_validate_lock"],"invariants":["LANGUAGE_DEPENDENCY_CONFLICTS_CLEAR"]},
      {"id":"language_repo_check","runner":"ordo_repo_check","phase":"PRE_EDITOR","required":True,"timeout_seconds":60,
       "depends_on":["compile"],"invariants":["LANGUAGE_PACKAGE_REFERENCES_VALID"]},
      {"id":"verification_truth","runner":"verification_truth","phase":"PRE_EDITOR","required":True,"timeout_seconds":30,
       "depends_on":["tests","language_validate_artifacts","language_consistency","language_validate_output"],
       "invariants":["VERIFICATION_REPORT_TRUTH","DECLARED_OUTPUT_EXECUTION_CLOSURE","NONVACUOUS_EVIDENCE"]},
      {"id":"editor_evidence","runner":"external_evidence","phase":"POST_EDITOR","required":True,"timeout_seconds":10,
       "args":{"path":"reports/EDITOR_RUN_EVIDENCE.json","accepted_statuses":["PASS","PASSED","SUCCESS"]},
       "invariants":["EDITOR_NATIVE_RUN_VERIFIED"]},
      {"id":"editor_evidence_quality","runner":"evidence_quality","phase":"POST_EDITOR","required":True,"timeout_seconds":30,
       "depends_on":["editor_evidence"],"args":{"report":"reports/EDITOR_RUN_EVIDENCE.json"},
       "invariants":["EDITOR_EVIDENCE_NON_VACUOUS"]},
      {"id":"strict_clean","runner":"ordo_clean_check","phase":"RELEASE","required":True,"timeout_seconds":90,
       "args":{"profile":"strict"},"depends_on":["editor_evidence_quality"],"invariants":["RELEASE_HYGIENE"]}
    ]
    target_cfg=root/"verification/RUNTIME_ADAPTER_TARGETS.json"
    adapter_targets=["chat_internal"]
    if target_cfg.is_file():
        td=json.loads(target_cfg.read_text(encoding="utf-8"))
        adapter_targets=[str(x) for x in (td.get("targets") or [])]
    if "editor_dev" not in adapter_targets:
        checks=[c for c in checks if c.get("id")!="generated_playbook_editor_adapter"]

    ext_path=root/"verification/PROFILE_EXTENSIONS.json"
    if ext_path.is_file():
        ext=json.loads(ext_path.read_text(encoding="utf-8"))
        extra=ext.get("checks",[])
        if not isinstance(extra,list):
            print(json.dumps({"status":"FAIL","code":"PROFILE_EXTENSIONS_CHECKS_NOT_LIST","path":str(ext_path)},indent=2)); return 2
        existing={c.get("id") for c in checks}
        for c in extra:
            if not isinstance(c,dict) or not c.get("id"):
                print(json.dumps({"status":"FAIL","code":"PROFILE_EXTENSION_INVALID","entry":c},indent=2)); return 2
            if c["id"] in existing:
                print(json.dumps({"status":"FAIL","code":"PROFILE_EXTENSION_DUPLICATE_ID","id":c["id"]},indent=2)); return 2
            checks.append(c); existing.add(c["id"])
    for c in checks:
        if int(c.get("timeout_seconds",60))>60 and not c.get("long_running_reason"):
            c["long_running_reason"]="bounded full/integration verification step; explicit alpha.44 watchdog exception"
    profile={"schema_version":"1.0","profile_id":f"{pkgid}-verification","playbook_revision":revision,"checks":checks}
    out=(root/a.output).resolve()
    try: out.relative_to(root)
    except Exception:
        print(json.dumps({"status":"FAIL","code":"OUTPUT_OUTSIDE_PACKAGE","path":str(out)},indent=2)); return 2
    out.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","output":str(out),"profile_id":profile["profile_id"],
                      "playbook_revision":revision,"checks":len(checks)},ensure_ascii=False,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
