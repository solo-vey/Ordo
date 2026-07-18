from copy import deepcopy
from pathlib import Path

from ordo.loader import load_yaml
from ordo.transition_provenance import validate_transition_provenance, validate_node_entry, build_node_context_envelope
from ordo.graph_validation import validate_process_graph


def source():
    return {
        "graph_contract": {"entry_node":"A", "transition_provenance":{"enabled":True,"mode":"strict"}},
        "nodes":[
            {"id":"A","entry_modes":["root"],"allowed_from":[],"on_answer":{"next":"B"},"node_context":{"required_state":["current_node"]}},
            {"id":"B","allowed_from":["A"],"terminal":True},
        ],
    }


def test_bidirectional_contract_passes():
    assert validate_transition_provenance(source())["status"] == "passed"


def test_outbound_only_edge_is_blocking():
    s=source(); s["nodes"][1]["allowed_from"]=[]
    r=validate_transition_provenance(s)
    assert r["status"] == "failed"
    assert any(i["code"]=="GRAPH_OUTBOUND_NOT_ACCEPTED" for i in r["issues"])


def test_inbound_only_edge_is_blocking():
    s=source(); s["nodes"][0]["on_answer"]={}
    r=validate_transition_provenance(s)
    assert any(i["code"]=="GRAPH_INBOUND_WITHOUT_OUTBOUND" for i in r["issues"])


def test_indirect_path_does_not_satisfy_direct_predecessor():
    s=source(); s["nodes"].insert(1,{"id":"X","allowed_from":["A"],"on_answer":{"next":"B"}}); s["nodes"][0]["on_answer"]={"next":"X"}; s["nodes"][2]["allowed_from"]=["A"]
    r=validate_transition_provenance(s)
    assert r["status"] == "failed"
    assert any(i["code"]=="GRAPH_OUTBOUND_NOT_ACCEPTED" and i["source_node"]=="X" for i in r["issues"])


def test_runtime_gate_blocks_invalid_predecessor():
    r=validate_node_entry(source(),target_node_id="B",previous_node_id="X")
    assert r["status"] == "blocked"
    assert r["issues"][0]["code"] == "RUNTIME_PREDECESSOR_NOT_ALLOWED"


def test_root_entry_requires_explicit_mode():
    assert validate_node_entry(source(),target_node_id="A",previous_node_id=None,entry_mode="root")["status"] == "passed"
    assert validate_node_entry(source(),target_node_id="B",previous_node_id=None,entry_mode="root")["status"] == "blocked"


def test_context_envelope_projects_only_declared_state():
    e=build_node_context_envelope(source(),{"current_node":"A","secret":"no"},"A")
    assert e["state_projection"] == {"current_node":"A"}
    assert "secret" not in e["state_projection"]


def test_apf_strict_transition_provenance_passes():
    root=Path(__file__).resolve().parents[2]
    s=load_yaml(root/'packages/ordo_applied_project_factory/source/program.ordo.yaml')
    r=validate_process_graph(s)
    assert r["status"] == "passed", r["issues"][:5]
    assert r["transition_provenance"]["status"] == "passed"


def test_compile_load_preserves_provenance_contract(tmp_path):
    from ordo.compiler import compile_source
    ir=compile_source(source())
    graph=next(op for op in ir["ops"] if op["op"]=="GRAPH.CONTRACT")
    node_b=next(op for op in ir["ops"] if op["op"]=="NODE.DEF" and op.get("source_local_id")=="B")
    assert graph["transition_provenance"]["enabled"] is True
    assert node_b["allowed_from"] == ["A"]

def test_invalid_entry_does_not_mutate_state():
    s=source(); state={"current_node":"B","previous_node_id":"X","value":"unchanged"}
    before=dict(state)
    r=validate_node_entry(s,target_node_id="B",previous_node_id=state["previous_node_id"])
    assert r["status"] == "blocked"
    assert state == before
