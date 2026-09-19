from __future__ import annotations

from ordo.node_decomposition import inspect_node_split, validate_node_responsibilities


def source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "demo.decomposition", "control_level": "standard", "execution_mode": "full_runtime"},
        "state": {"schema": {"title": ""}},
        "graph_contract": {"entry_node": "N_COMPOUND", "allowed_cycle_regions": [{"id": "R_RETRY", "nodes": ["N_COMPOUND", "G_READY"]}]},
        "node_responsibility_policy": {"mode": "strict"},
        "state_lineage": {
            "mode": "strict",
            "fields": [{"path": "title", "shape": "string", "owner": "N_COMPOUND", "collection_mode": "analyst_answer", "consumers": ["G_READY"]}],
        },
        "nodes": [
            {
                "id": "N_COMPOUND",
                "question": "Collect, analyse, draft, confirm and route.",
                "responsibility_kinds": ["collection", "analysis", "drafting", "confirmation", "routing"],
                "on_answer": {"update_state": {"title": "$answer"}, "next": "G_READY"},
            },
            {"id": "N_DONE", "terminal": True},
        ],
        "gates": [{"id": "G_READY", "condition": "state.title != ''", "on_pass": "N_DONE", "on_fail": "N_COMPOUND"}],
    }


def test_strict_policy_rejects_a_compound_node() -> None:
    report = validate_node_responsibilities(source())
    assert report["status"] == "failed"
    finding = report["issues"][0]
    assert finding["code"] == "NODE_RESPONSIBILITY_COMPOUND"
    assert finding["responsibilities"] == ["collection", "analysis", "drafting", "confirmation", "routing"]


def test_split_impact_preserves_graph_lineage_gate_and_cycle_surfaces() -> None:
    report = inspect_node_split(source(), "N_COMPOUND", replacement_ids=["N_COLLECT", "N_ANALYSE"])
    assert report["status"] == "passed", report
    surface = report["preservation_surface"]
    assert surface["incoming_edges"] == ["G_READY"]
    assert surface["outgoing_edges"] == ["G_READY"]
    assert surface["gate_bindings"] == ["G_READY"]
    assert surface["state_writes"] == ["title"]
    assert surface["state_lineage_owner_paths"] == ["title"]
    assert surface["cycle_components"] == [["G_READY", "N_COMPOUND"]]
    assert report["source_mutated"] is False


def test_non_colliding_single_responsibility_node_passes_strict_policy() -> None:
    value = source()
    value["nodes"][0]["responsibility_kinds"] = ["collection"]
    assert validate_node_responsibilities(value)["status"] == "passed"
