from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from ordo.compiler import compile_source
from ordo.graph_topology import graph_topology
from ordo.graph_validation import validate_process_graph
from ordo.registry_checks import validate_ir_opcodes
from ordo.transition_provenance import validate_dynamic_route


ROOT = Path(__file__).resolve().parents[2]


def graph_source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "example.graph", "control_level": "standard", "execution_mode": "full_runtime"},
        "nodes": [
            {
                "id": "N_START",
                "on_answer": {"continue": {"next": "G_CHECK"}},
                "transitions": [{"id": "T_START", "to": "G_CHECK"}],
                "navigation_contract": {"allowed_from": [], "allowed_to": ["G_CHECK"]},
            },
            {"id": "N_RECOVERY", "navigation_contract": {"allowed_from": ["G_CHECK"]}},
            {"id": "N_DONE", "terminal": True, "navigation_contract": {"allowed_from": ["G_CHECK", "N_RECOVERY"]}},
        ],
        "gates": [{
            "id": "G_CHECK", "method": "mechanical", "trust_class": "deterministic", "condition": "state.ready is true",
            "pass_to": "N_DONE", "fail_to": "N_RECOVERY", "navigation_contract": {"allowed_from": ["N_START"]},
        }],
        "graph_contract": {
            "entry_node": "N_START",
            "bidirectional_transition_policy": "explicit_source_and_target",
            "incoming_edge_field": "allowed_from",
            "external_terminal_targets": [],
            "allowed_cycle_regions": [],
            "deleted_ids": ["N_LEGACY_RECOVERY"],
            "dynamic_routes": [{
                "id": "ROUTE_RECOVERY_RETURN", "kind": "recovery", "from": "N_RECOVERY",
                "route_key": "validated_return_target", "allowed_targets": ["N_DONE"],
                "on_invalid_route": "block_and_keep_current_node", "max_hops": 1,
            }],
        },
    }


def codes(report: dict) -> set[str]:
    return {issue["code"] for issue in report["issues"]}


def test_canonical_transition_forms_are_one_graph_contract() -> None:
    source = graph_source()
    topology = graph_topology(source)
    assert set(topology["adjacency"]["N_START"]) == {"G_CHECK"}
    assert set(topology["adjacency"]["G_CHECK"]) == {"N_DONE", "N_RECOVERY"}
    assert topology["adjacency"]["N_RECOVERY"] == ["N_DONE"]
    report = validate_process_graph(source)
    assert report["status"] == "passed", report
    assert report["summary"]["dynamic_routes"] == 1


def test_dynamic_route_is_allowlisted_bounded_and_runtime_verified() -> None:
    source = graph_source()
    assert validate_dynamic_route(source, source_node_id="N_RECOVERY", route_key="validated_return_target", target_node_id="N_DONE")["status"] == "passed"
    forbidden = validate_dynamic_route(source, source_node_id="N_RECOVERY", route_key="validated_return_target", target_node_id="N_START")
    assert forbidden["issues"][0]["code"] == "RUNTIME_DYNAMIC_ROUTE_TARGET_FORBIDDEN"
    bounded = validate_dynamic_route(source, source_node_id="N_RECOVERY", route_key="validated_return_target", target_node_id="N_DONE", hops=2)
    assert bounded["issues"][0]["code"] == "RUNTIME_DYNAMIC_ROUTE_BOUND_EXCEEDED"


def test_graph_contract_rejects_invalid_dynamic_and_deleted_id_forms() -> None:
    source = graph_source()
    source["graph_contract"]["dynamic_routes"][0]["allowed_targets"] = ["N_MISSING"]
    source["graph_contract"]["dynamic_routes"][0]["max_hops"] = 0
    source["graph_contract"]["deleted_ids"].append("N_DONE")
    report = validate_process_graph(source)
    assert {"GRAPH_TARGET_MISSING", "GRAPH_DYNAMIC_ROUTE_BOUND_REQUIRED", "GRAPH_DELETED_ID_REUSED"} <= codes(report)

    source = graph_source()
    source["nodes"][0]["on_answer"]["continue"]["next"] = "N_LEGACY_RECOVERY"
    report = validate_process_graph(source)
    assert "GRAPH_TARGET_DELETED" in codes(report)


def test_duplicate_list_transition_is_rejected_in_its_own_scope() -> None:
    source = graph_source()
    source["nodes"][0]["transitions"] = [{"to": "G_CHECK"}, {"to": "G_CHECK"}]
    report = validate_process_graph(source)
    assert "GRAPH_TRANSITION_DUPLICATE" in codes(report)


def test_compiler_preserves_contract_and_emits_dynamic_route_opcode() -> None:
    ir = compile_source(deepcopy(graph_source()))
    route = next(op for op in ir["ops"] if op["op"] == "GRAPH.ROUTE.DEF")
    assert route["route_key"] == "validated_return_target"
    assert route["allowed_targets"] == ["N_DONE"]
    gate = next(op for op in ir["ops"] if op["op"] == "GATE.DEF")
    assert gate["pass_to"] == "N_DONE"
    assert gate["fail_to"] == "N_RECOVERY"
    node = next(op for op in ir["ops"] if op.get("source_local_id") == "N_START")
    assert node["navigation_contract"]["allowed_to"] == ["G_CHECK"]
    assert validate_ir_opcodes(ir, ROOT)["status"] == "passed"
