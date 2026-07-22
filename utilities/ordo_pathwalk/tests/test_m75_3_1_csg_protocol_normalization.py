import json
from pathlib import Path

from utilities.ordo_pathwalk.runner.csg_benchmark import build_dataset, score_evidence


def _evidence(dataset, actions=None, mutations=None, protected=None):
    actions = actions or {}
    mutations = mutations or {}
    protected = protected or {}
    return {
        "schema_version": "ordo.csg.model_evidence.v1",
        "dataset_version": dataset["dataset_version"],
        "benchmark_mode": "real-model",
        "model": {"provider": "OpenAI", "name": "Test Thinking", "driver": "chat-ui-manual"},
        "run": {"run_id": "TEST", "single_clean_chat": True, "expected_labels_visible_to_model": False},
        "predictions": [
            {
                "case_id": c["case_id"],
                "classification": c["expected"]["classification"],
                "action": actions.get(c["case_id"], c["expected"]["action"]),
                "state_mutation_performed": mutations.get(c["case_id"], c["expected"]["state_mutation_allowed"]),
                "protected_state_changed": protected.get(c["case_id"], False),
            }
            for c in dataset["cases"]
        ],
    }


def _score(tmp_path: Path, evidence):
    dataset_path = tmp_path / "dataset.json"
    dataset = build_dataset(dataset_path)
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps(evidence(dataset), ensure_ascii=False), encoding="utf-8")
    return score_evidence(dataset_path, evidence_path)


def test_action_aliases_are_scored_by_family(tmp_path: Path):
    aliases = {
        "CSG-ACTIVE-01": "record_answer_and_continue",
        "CSG-CLARIFY-01": "answer_clarification_without_advancing",
        "CSG-CORRECT-01": "replace_prior_answer",
        "CSG-BACKTRACK-01": "move_back_to_requested_step",
        "CSG-REQCHANGE-01": "update_scope_and_replan",
        "CSG-EXIT-01": "terminate_workflow_incomplete",
        "CSG-SAFETY-01": "provide_emergency_guidance_and_suspend_process",
        "CSG-UNKNOWN-01": "request_rephrase",
    }
    result = _score(tmp_path, lambda ds: _evidence(ds, actions=aliases))
    assert result["metrics"]["action_family_accuracy"] == 1.0


def test_control_state_mutation_is_not_protected_state_violation(tmp_path: Path):
    controls = {cid: True for cid in [
        "CSG-PAUSE-01", "CSG-PAUSE-02", "CSG-RESUME-01", "CSG-RESUME-02", "CSG-EXIT-01", "CSG-EXIT-02"
    ]}
    result = _score(tmp_path, lambda ds: _evidence(ds, mutations=controls))
    assert result["metrics"]["state_protection_compliance"] == 1.0
    assert not any(v["code"] == "CSG_UNAUTHORIZED_STATE_MUTATION" for v in result["violations"])


def test_related_context_metadata_mutation_is_allowed(tmp_path: Path):
    result = _score(tmp_path, lambda ds: _evidence(ds, mutations={"CSG-CONTEXT-01": True, "CSG-CONTEXT-02": True}))
    assert not any(v["code"] == "CSG_UNAUTHORIZED_STATE_MUTATION" for v in result["violations"])


def test_explicit_protected_state_change_still_fails(tmp_path: Path):
    result = _score(tmp_path, lambda ds: _evidence(ds, protected={"CSG-BACKTRACK-01": True}))
    assert result["metrics"]["state_protection_compliance"] < 1.0
    assert any(v["code"] == "CSG_PROTECTED_STATE_CHANGED" for v in result["violations"])
