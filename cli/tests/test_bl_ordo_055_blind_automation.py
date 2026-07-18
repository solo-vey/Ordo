from pathlib import Path
import importlib.util, yaml, sys

MODULE = Path(__file__).parents[1] / "ordo" / "blind_automation.py"
spec=importlib.util.spec_from_file_location("blind_automation", MODULE)
m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)
ROOT=Path(__file__).parents[2]

def load(name): return yaml.safe_load((ROOT/"language/examples"/name).read_text())

def test_profiles_validate():
    assert m.validate_profile(load("blind_automation_step_bound.yaml")) == []
    assert m.validate_profile(load("blind_automation_semantic_adaptive.yaml")) == []

def test_self_scoring_fails_closed():
    p=load("blind_automation_semantic_adaptive.yaml");p["self_scoring"]=True
    assert "self_scoring must be false" in m.validate_profile(p)

def test_step_disclosure_binding_required():
    p=load("blind_automation_step_bound.yaml");p["step_disclosure_bindings"].pop("collect_source")
    assert any("every step" in e for e in m.validate_profile(p))

def test_semantic_minimal_disclosure():
    s=m.BlindRunState(load("blind_automation_semantic_adaptive.yaml"))
    s.set_fact("document_id","D1");s.set_fact("secret_answer","hidden")
    assert s.disclose(["document_id","secret_answer"],{"document_id"}) == {"document_id":"D1"}

def test_correction_invalidates_artifact_and_approval():
    s=m.BlindRunState(load("blind_automation_step_bound.yaml"));s.set_fact("document_id","D1")
    s.register_artifact("passport","v1",["document_id"]);s.validate_artifact("passport","v1");s.approve("passport","v1")
    assert s.finish(["document_id"],["passport"]) == "T_COMPLETED"
    s.set_fact("document_id","D2")
    assert s.artifacts["passport"][0]["status"] == "stale"
    assert s.approvals[("passport","v1")] == "invalidated"
    assert s.finish(["document_id"],["passport"]) == "not_ready"

def test_approval_does_not_transfer_versions():
    s=m.BlindRunState(load("blind_automation_step_bound.yaml"));s.set_fact("document_id","D1")
    s.register_artifact("passport","v1",["document_id"]);s.validate_artifact("passport","v1");s.approve("passport","v1")
    s.register_artifact("passport","v2",["document_id"]);s.validate_artifact("passport","v2")
    assert s.finish(["document_id"],["passport"]) == "not_ready"

def test_diagnostic_requires_evidence_for_corroborated_status():
    claim={"status":"trace_corroborated","source_node":"N1","loaded_assets":{},"confirmed_evidence":[],"gate_path":[],"suspected_component":"validator"}
    assert "corroborated status requires evidence_refs" in m.validate_diagnostic_claim(claim)

def test_model_reported_claim_allowed_without_corroboration_but_not_closed():
    claim={"status":"model_reported","source_node":"N1","loaded_assets":{},"confirmed_evidence":[],"gate_path":[],"suspected_component":"prompt"}
    assert m.validate_diagnostic_claim(claim) == []

def test_terminal_vocab_is_exact():
    assert m.TERMINAL_STATES == {"T_COMPLETED","T_INPUT_BLOCKED","T_SCENARIO_EXHAUSTED","NO_GO","not_ready"}

def test_source_reference_preserved():
    assert (ROOT/"language/improvement_intake/bl_ordo_055_references/ORDO_BLIND_AUTOMATION_STANDARD_AND_PLAYBOOK_IMPROVEMENT_UA.docx").exists()
