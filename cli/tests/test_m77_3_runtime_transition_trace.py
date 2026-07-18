from pathlib import Path

import pytest
import yaml

from ordo.compiler import compile_source
from ordo.flow_reuse_runtime import (
    FlowReuseRuntimeError,
    enter_shared_tail,
    exit_shared_tail,
    transition_through_join,
)

ROOT = Path(__file__).resolve().parents[2]


def compiled_ops():
    source = yaml.safe_load((ROOT / "language/examples/source/optional_flow_reuse_example.ordo.yaml").read_text())
    source["ordo"] = {"package": "example.flow", "version": "0.12.0"}
    return compile_source(source)["ops"]


def one(op):
    return next(x for x in compiled_ops() if x["op"] == op)


def test_join_transitions_to_target_and_preserves_selected_branch_provenance():
    join = one("FLOW.JOIN.DEF")
    result = transition_through_join(
        join,
        branch_alias="approved",
        incoming_state={"package_id": "P1", "review_status": "approved"},
    )
    assert result.next_node == "package.close.NODE.PACKAGE.FINALIZE"
    assert result.state == {"package_id": "P1", "review_status": "approved"}
    assert result.provenance["join_inputs"][0]["incoming_alias"] == "approved"
    assert [x["event"] for x in result.trace] == [
        "flow_join_entered", "flow_join_state_merged", "flow_join_exited"
    ]


def test_join_rejects_unknown_or_ambiguous_incoming_branch():
    join = one("FLOW.JOIN.DEF")
    with pytest.raises(FlowReuseRuntimeError, match="unambiguous incoming branch"):
        transition_through_join(join, branch_alias="missing", incoming_state={})


def test_join_requires_contract_fields():
    join = one("FLOW.JOIN.DEF")
    with pytest.raises(FlowReuseRuntimeError, match="missing required fields"):
        transition_through_join(join, branch_alias="approved", incoming_state={"package_id": "P1"})


def test_join_fails_closed_on_protected_field_conflict():
    join = one("FLOW.JOIN.DEF")
    with pytest.raises(FlowReuseRuntimeError, match="protected field conflict"):
        transition_through_join(
            join,
            branch_alias="approved",
            accumulated_state={"package_id": "P1"},
            incoming_state={"package_id": "P2", "review_status": "approved"},
        )


def test_join_does_not_leak_branch_local_fields():
    join = one("FLOW.JOIN.DEF")
    result = transition_through_join(
        join,
        branch_alias="approved",
        incoming_state={"package_id": "P1", "review_status": "approved", "reviewer_comment": "private"},
    )
    assert "reviewer_comment" not in result.state


def test_shared_tail_imports_only_allowed_state_and_keeps_path_history():
    ref = one("SHARED.TAIL.REFERENCE.RESOLVED")
    result = enter_shared_tail(
        ref,
        caller_state={"package_id": "P1", "review_status": "approved", "secret": "x"},
        path_history=["NODE.A", "NODE.B"],
    )
    assert result.next_node == "package.close.NODE.PACKAGE.FINALIZE"
    assert result.state == {"package_id": "P1", "review_status": "approved"}
    assert result.provenance["path_history"] == ["NODE.A", "NODE.B", ref["tail_id"]]
    assert result.provenance["protected_snapshot"] == {"package_id": "P1"}


def test_shared_tail_import_requires_required_fields():
    ref = one("SHARED.TAIL.REFERENCE.RESOLVED")
    with pytest.raises(FlowReuseRuntimeError, match="missing required fields"):
        enter_shared_tail(ref, caller_state={"package_id": "P1"})


def test_shared_tail_exports_only_declared_fields_and_restores_caller_context():
    ref = one("SHARED.TAIL.REFERENCE.RESOLVED")
    entered = enter_shared_tail(
        ref,
        caller_state={"package_id": "P1", "review_status": "approved", "caller_only": 7},
        path_history=["NODE.A"],
    )
    exited = exit_shared_tail(
        ref,
        tail_state={"package_status": "closed", "report_id": "R1", "internal": "no"},
        caller_state={"package_id": "P1", "review_status": "approved", "caller_only": 7},
        provenance=entered.provenance,
        next_node="NODE.AFTER.CLOSE",
    )
    assert exited.next_node == "NODE.AFTER.CLOSE"
    assert exited.state == {
        "package_id": "P1", "review_status": "approved", "caller_only": 7,
        "package_status": "closed", "report_id": "R1",
    }
    assert exited.provenance["tail_exit"]["exported_fields"] == ["package_status", "report_id"]


def test_shared_tail_cannot_overwrite_protected_caller_field():
    ref = one("SHARED.TAIL.REFERENCE.RESOLVED")
    ref = dict(ref)
    ref["export_state"] = {"allow": ["package_id"], "rename": {}}
    entered = enter_shared_tail(ref, caller_state={"package_id": "P1", "review_status": "approved"})
    with pytest.raises(FlowReuseRuntimeError, match="overwrite protected field"):
        exit_shared_tail(
            ref,
            tail_state={"package_id": "P2"},
            caller_state={"package_id": "P1", "review_status": "approved"},
            provenance=entered.provenance,
            next_node="NODE.X",
        )


def test_runtime_functions_do_not_mutate_input_state():
    join = one("FLOW.JOIN.DEF")
    state = {"package_id": "P1", "review_status": "approved"}
    transition_through_join(join, branch_alias="approved", incoming_state=state)
    assert state == {"package_id": "P1", "review_status": "approved"}


def test_shared_tail_blocks_recursive_entry():
    ref = one("SHARED.TAIL.REFERENCE.RESOLVED")
    with pytest.raises(FlowReuseRuntimeError, match="recursive shared-tail entry blocked"):
        enter_shared_tail(ref, caller_state={"package_id": "P1", "review_status": "approved"}, path_history=[ref["tail_id"]])


def test_shared_tail_blocks_excessive_call_depth():
    ref = dict(one("SHARED.TAIL.REFERENCE.RESOLVED"))
    ref["max_call_depth"] = 2
    with pytest.raises(FlowReuseRuntimeError, match="call depth exceeded"):
        enter_shared_tail(ref, caller_state={"package_id": "P1", "review_status": "approved"}, path_history=["TAIL.A", "TAIL.B"])


def test_shared_tail_uses_declared_return_target_when_not_overridden():
    ref = one("SHARED.TAIL.REFERENCE.RESOLVED")
    entered = enter_shared_tail(ref, caller_state={"package_id": "P1", "review_status": "approved"})
    exited = exit_shared_tail(
        ref,
        tail_state={"package_status": "closed", "report_id": "R1"},
        caller_state={"package_id": "P1", "review_status": "approved"},
        provenance=entered.provenance,
    )
    assert exited.next_node == ref["return_to"]
