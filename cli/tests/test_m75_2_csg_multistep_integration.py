from __future__ import annotations

import copy

from ordo.csg_runtime import enforce_csg_proposal


CSG = {
    "supported": True,
    "enabled": True,
    "mode": "guided_redirect",
    "state_change_on_out_of_scope": False,
}


def test_multistep_process_preserves_state_through_noise_pause_safety_and_resume():
    state = {
        "current_node": "N_ALIAS",
        "path": "A1",
        "contract": {"alias": None, "source_field": None},
        "passed_gates": [],
    }

    r1 = enforce_csg_proposal(CSG, state, {
        "classification": "answer_to_active_question",
        "action": "accept_answer",
        "state_update": {"contract.alias": "LU_CHANGE_STATE"},
        "target_node": "N_SOURCE_FIELD",
    })
    assert r1["status"] == "applied"
    assert state["contract"]["alias"] == "LU_CHANGE_STATE"

    stable = copy.deepcopy(state)
    r2 = enforce_csg_proposal(CSG, state, {
        "classification": "unrelated_topic",
        "action": "redirect",
        "state_update": {"contract.alias": "CORRUPTED"},
        "target_node": "N_OUTPUT",
    })
    assert r2["status"] == "blocked"
    assert state == stable

    r3 = enforce_csg_proposal(CSG, state, {
        "classification": "pause_request",
        "action": "pause_process",
    })
    assert r3["status"] == "applied"
    assert state["_csg_runtime"]["status"] == "paused"

    paused = copy.deepcopy(state)
    r4 = enforce_csg_proposal(CSG, state, {
        "classification": "unsafe_or_emergency_message",
        "action": "bypass_for_safety",
    })
    assert r4["status"] == "applied"
    assert state["contract"] == paused["contract"]
    assert state["current_node"] == paused["current_node"]

    r5 = enforce_csg_proposal(CSG, state, {
        "classification": "answer_to_active_question",
        "action": "accept_answer",
        "state_update": {"contract.source_field": "company.status"},
    })
    assert r5["status"] == "blocked"
    assert r5["issues"][0]["code"] == "CSG_PROCESS_PAUSED"

    r6 = enforce_csg_proposal(CSG, state, {
        "classification": "resume_request",
        "action": "resume_process",
    })
    assert r6["status"] == "applied"
    assert state["current_node"] == "N_SOURCE_FIELD"

    r7 = enforce_csg_proposal(CSG, state, {
        "classification": "answer_to_active_question",
        "action": "accept_answer",
        "state_update": {"contract.source_field": "company.status"},
        "target_node": "N_CONFIRM",
    })
    assert r7["status"] == "applied"
    assert state["contract"] == {
        "alias": "LU_CHANGE_STATE",
        "source_field": "company.status",
    }
    assert state["current_node"] == "N_CONFIRM"


def test_requirement_change_reopens_flow_and_exit_prevents_further_execution():
    state = {
        "current_node": "N_CONFIRM",
        "path": "A1",
        "contract": {"deliverable": "full_package", "confirmed": True},
        "blocked": False,
    }

    changed = enforce_csg_proposal(CSG, state, {
        "classification": "requirement_change",
        "action": "reopen_contract",
        "state_update": {
            "contract.deliverable": "qa_only",
            "contract.confirmed": False,
        },
        "target_node": "N_OUTPUT_SCOPE",
    })
    assert changed["status"] == "applied"
    assert state["contract"]["deliverable"] == "qa_only"
    assert state["contract"]["confirmed"] is False
    assert state["current_node"] == "N_OUTPUT_SCOPE"

    exited = enforce_csg_proposal(CSG, state, {
        "classification": "exit_request",
        "action": "exit_process",
    })
    assert exited["status"] == "applied"
    assert state["go_no_go"] == "incomplete"

    after = copy.deepcopy(state)
    blocked = enforce_csg_proposal(CSG, state, {
        "classification": "answer_to_active_question",
        "action": "accept_answer",
        "state_update": {"contract.confirmed": True},
    })
    assert blocked["status"] == "blocked"
    assert state == after
