from pathlib import Path
import re

import alpha20_runtime as rt
import editor_service as es


def test_statepatch_rejects_unresolved_runtime_expression_scalar():
    state={"implementation_prompt_open_questions":[]}
    patch={"base_revision":0,"operations":[{"op":"set","path":"implementation_prompt_open_questions","value":"$remaining_unresolved_questions","basis":"derived","reason":"fixture"}]}
    new, status=rt.apply_state_patch_atomic(state,patch,allowed_paths=["implementation_prompt_open_questions"],current_revision=0)
    assert not status["committed"]
    assert any("unresolved runtime expression" in x for x in status["errors"])
    assert new==state


def test_statepatch_rejects_nested_unresolved_runtime_expression():
    state={"x":{}}
    patch={"base_revision":0,"operations":[{"op":"set","path":"x","value":{"when":"$runtime.timestamp"},"basis":"derived","reason":"fixture"}]}
    new,status=rt.apply_state_patch_atomic(state,patch,allowed_paths=["x"],current_revision=0)
    assert not status["committed"]
    assert any("operations[0].value.when" in x for x in status["errors"])


def test_deterministic_human_route_resolves_runtime_timestamp():
    rec={"on_answer":{"approve":{"update_state":{"analyst_reviewed_at":"$runtime.timestamp"}}}}
    new,updates=es._apply_direct_answer_updates(rec,{},"approve")
    value=updates["analyst_reviewed_at"]
    assert value != "$runtime.timestamp"
    assert re.match(r"^20\d\d-\d\d-\d\dT", value)
    assert new["analyst_reviewed_at"]==value
