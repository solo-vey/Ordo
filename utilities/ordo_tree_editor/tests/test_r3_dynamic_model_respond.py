from utilities.ordo_tree_editor.editor_service import _semantic_model_phase_enabled


def test_semantic_model_enter_only_plan_accepts_dynamic_respond():
    traits = {
        "model_executed": True,
        "model_executed_phases": ["enter"],
        "runtime_executor": "semantic_model",
    }
    assert _semantic_model_phase_enabled(traits, "enter") is True
    assert _semantic_model_phase_enabled(traits, "respond") is True


def test_non_model_executor_does_not_gain_dynamic_respond():
    traits = {
        "model_executed": False,
        "model_executed_phases": [],
        "runtime_executor": "artifact_presenter",
    }
    assert _semantic_model_phase_enabled(traits, "respond") is False


def test_unrelated_phase_is_not_authorized():
    traits = {
        "model_executed": True,
        "model_executed_phases": ["enter"],
        "runtime_executor": "semantic_model",
    }
    assert _semantic_model_phase_enabled(traits, "finalize") is False
