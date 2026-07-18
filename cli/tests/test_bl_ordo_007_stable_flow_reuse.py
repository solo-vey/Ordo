from pathlib import Path
import yaml

from ordo.compiler import compile_source, lower_flow_reuse

ROOT = Path(__file__).resolve().parents[2]


def load(rel):
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def test_two_real_packages_provide_stable_optional_flow_reuse_evidence():
    apf = load("packages/ordo_applied_project_factory/source/program.ordo.yaml")
    hybrid = load("packages/ordo_hybrid_executor/source/program.ordo.yaml")
    assert apf["flow_reuse"]["maturity"] == "stable_optional"
    assert hybrid["flow_reuse"]["maturity"] == "stable_optional"
    assert len(apf["flow_reuse"]["references"]) >= 2
    assert len(hybrid["flow_reuse"]["references"]) >= 1


def test_hybrid_executor_reuse_matches_existing_convergence():
    src = load("packages/ordo_hybrid_executor/source/program.ordo.yaml")
    nodes = {n["id"]: n for n in src["nodes"]}
    assert nodes["N_LOAD_IR"]["on_answer"]["next"] == "N_CLASSIFY_INPUT"
    assert nodes["N_NEXT_MOVE"]["on_answer"]["next"] == "N_CLASSIFY_INPUT"
    join = src["flow_reuse"]["joins"][0]
    assert {x["node"] for x in join["incoming"]} == {"N_LOAD_IR", "N_NEXT_MOVE"}
    assert join["target"]["node"] == "N_CLASSIFY_INPUT"


def test_hybrid_executor_flow_reuse_lowers_deterministically():
    src = load("packages/ordo_hybrid_executor/source/program.ordo.yaml")
    first = lower_flow_reuse(src, "ordo.hybrid.executor")
    second = lower_flow_reuse(src, "ordo.hybrid.executor")
    assert first == second
    ref = next(x for x in first if x["op"] == "SHARED.TAIL.REFERENCE.RESOLVED")
    assert ref["return_to"] == "N_NEXT_MOVE"
    assert ref["max_call_depth"] == 16


def test_compiled_ir_preserves_stable_flow_reuse_contract():
    src = load("packages/ordo_hybrid_executor/source/program.ordo.yaml")
    ir = compile_source(src)
    assert any(x["op"] == "FLOW.JOIN.DEF" for x in ir["ops"])
    assert any(x["op"] == "SHARED.TAIL.REFERENCE.RESOLVED" for x in ir["ops"])


def test_stable_reference_requires_return_target():
    src = load("packages/ordo_hybrid_executor/source/program.ordo.yaml")
    del src["flow_reuse"]["references"][0]["return_to"]
    import pytest
    from ordo.compiler import FlowReuseCompileError
    with pytest.raises(FlowReuseCompileError, match="requires deterministic return_to"):
        lower_flow_reuse(src, "ordo.hybrid.executor")
