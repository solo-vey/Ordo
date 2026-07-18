from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from ordo.compiler import FlowReuseCompileError, compile_source, lower_flow_reuse

ROOT = Path(__file__).resolve().parents[2]


def example():
    src = yaml.safe_load((ROOT / "language/examples/source/optional_flow_reuse_example.ordo.yaml").read_text())
    src["ordo"] = {"package": "example.flow", "version": "0.12.0"}
    return src


def ops_by(ir, op):
    return [item for item in ir["ops"] if item["op"] == op]


def test_join_lowers_to_synthetic_node_and_explicit_edges():
    ir = compile_source(example())
    joins = ops_by(ir, "FLOW.JOIN.DEF")
    assert len(joins) == 1
    join = joins[0]
    assert join["id"] == "package.review.JOIN.REVIEW.COMPLETE"
    assert join["target"] == "package.close.NODE.PACKAGE.FINALIZE"
    assert join["lowered_node"].endswith(".__join__")
    edges = [x for x in ops_by(ir, "FLOW.EDGE") if x.get("join_id") == join["id"]]
    assert len(edges) == 3
    assert {x["edge_kind"] for x in edges} == {"join_incoming", "join_target"}


def test_reference_resolves_to_qualified_tail_entry_and_preserves_provenance():
    ir = compile_source(example())
    refs = ops_by(ir, "SHARED.TAIL.REFERENCE.RESOLVED")
    assert len(refs) == 1
    ref = refs[0]
    assert ref["tail_id"] == "package.close.TAIL.PACKAGE.CLOSE"
    assert ref["resolved_entry"] == "package.close.NODE.PACKAGE.FINALIZE"
    assert ref["resolved_nodes"] == [
        "package.close.NODE.PACKAGE.FINALIZE",
        "package.close.NODE.PACKAGE.REPORT",
    ]
    assert ref["source_provenance"]["reference"]["id"] == "REF.PACKAGE.CLOSE"
    assert ref["source_provenance"]["tail"]["id"] == "TAIL.PACKAGE.CLOSE"


def test_lowering_is_deterministic_except_compile_timestamp_and_canary():
    source = example()
    before = deepcopy(source)
    first = lower_flow_reuse(source, "example.flow")
    second = lower_flow_reuse(source, "example.flow")
    assert first == second
    assert source == before


def test_missing_tail_fails_closed():
    source = example()
    source["flow_reuse"]["references"][0]["tail_id"] = "TAIL.MISSING"
    with pytest.raises(FlowReuseCompileError, match="missing shared tail"):
        compile_source(source)


def test_reference_entry_must_match_tail_entry():
    source = example()
    source["flow_reuse"]["references"][0]["entry"] = "NODE.OTHER"
    with pytest.raises(FlowReuseCompileError, match="entry does not match"):
        compile_source(source)


def test_explicit_map_must_be_complete_and_one_to_one():
    source = example()
    source["flow_reuse"]["references"][0]["namespace_map"] = {}
    with pytest.raises(FlowReuseCompileError, match="complete explicit namespace map"):
        compile_source(source)

    source = example()
    source["flow_reuse"]["references"][0]["namespace_map"] = {
        "package.review": "package.close",
        "package.other": "package.close",
    }
    with pytest.raises(FlowReuseCompileError, match="one-to-one"):
        compile_source(source)


def test_inherit_cannot_cross_namespaces():
    source = example()
    ref = source["flow_reuse"]["references"][0]
    ref["namespace_policy"] = "inherit"
    ref.pop("namespace_map", None)
    with pytest.raises(FlowReuseCompileError, match="cannot inherit across namespaces"):
        compile_source(source)


def test_duplicate_ids_fail_closed():
    source = example()
    duplicate = deepcopy(source["flow_reuse"]["references"][0])
    source["flow_reuse"]["references"].append(duplicate)
    with pytest.raises(FlowReuseCompileError, match="duplicate flow reuse id"):
        compile_source(source)


def test_rename_maps_must_be_one_to_one():
    source = example()
    source["flow_reuse"]["references"][0]["import_state"]["rename"] = {
        "a": "x",
        "b": "x",
    }
    with pytest.raises(FlowReuseCompileError, match="import_state.rename must be one-to-one"):
        compile_source(source)


def test_recursive_shared_tail_dependency_fails_closed():
    source = example()
    tail = source["flow_reuse"]["shared_tails"][0]
    tail["references"] = [{
        "tail_id": tail["id"],
        "tail_namespace": tail["namespace"],
    }]
    with pytest.raises(FlowReuseCompileError, match="recursive shared-tail reference"):
        compile_source(source)


def test_indirect_recursive_shared_tail_dependency_fails_closed():
    source = example()
    first = source["flow_reuse"]["shared_tails"][0]
    second = {
        "id": "TAIL.PACKAGE.SECOND",
        "namespace": "package.close",
        "entry": "NODE.PACKAGE.SECOND",
        "nodes": ["NODE.PACKAGE.SECOND"],
        "references": [{"tail_id": first["id"], "tail_namespace": first["namespace"]}],
    }
    first["references"] = [{"tail_id": second["id"], "tail_namespace": second["namespace"]}]
    source["flow_reuse"]["shared_tails"].append(second)
    with pytest.raises(FlowReuseCompileError, match="recursive shared-tail reference"):
        compile_source(source)
