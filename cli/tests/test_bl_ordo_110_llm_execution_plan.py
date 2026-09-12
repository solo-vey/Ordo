from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import shutil
import tempfile

import yaml

from ordo.compiler import compile_source
from ordo.cli import main
from ordo.llm_execution_plan import build_llm_execution_plan, semantic_ir_sha256, validate_llm_execution_plan


ROOT = Path(__file__).resolve().parents[2]


def source() -> dict:
    return {
        "ordo": {"version": "0.12", "package": "demo.plan", "control_level": "standard", "execution_mode": "full_runtime"},
        "state": {"schema": {"name": {"type": "string"}, "fixed_locale": {"type": "string", "immutable": True, "default": "en"}}},
        "resources": [
            {"id": "R_BASE", "kind": "reference"},
            {"id": "R_CHILD", "kind": "reference", "depends_on": ["R_BASE"]},
        ],
        "nodes": [{"id": "N_START", "question": "What is the name?", "answer_type": "text", "required_fields": ["name", "fixed_locale"], "resources": ["R_CHILD"], "transitions": {"next": "G_READY"}}],
        "gates": [{"id": "G_READY", "method": "mechanical", "condition": "state.name != null", "on_pass": "STOP_DONE", "on_fail": "$stay"}],
        "terminals": ["STOP_DONE"],
    }


def write_inputs(tmp_path: Path, src: dict) -> tuple[Path, Path, Path]:
    source_path = tmp_path / "program.ordo.yaml"
    source_path.write_text(yaml.safe_dump(src, sort_keys=False), encoding="utf-8")
    ir_path = tmp_path / "program.ir.json"
    ir_path.write_text(json.dumps(compile_source(src), sort_keys=True), encoding="utf-8")
    plan_path = tmp_path / "llm_execution_plan.json"
    import hashlib
    plan = build_llm_execution_plan(src, source_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(), ir_sha256=semantic_ir_sha256(ir_path))
    plan_path.write_text(json.dumps(plan, sort_keys=True), encoding="utf-8")
    return source_path, ir_path, plan_path


def test_plan_is_compact_and_excludes_default_satisfiable_immutable_dependency(tmp_path: Path) -> None:
    source_path, ir_path, plan_path = write_inputs(tmp_path, source())
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    phase = plan["phases"][0]
    assert phase["classification"] == "llm"
    assert phase["projected_state"] == ["name"]
    assert phase["projected_resources"] == ["R_CHILD"]
    assert "state" not in phase["instruction"]
    assert validate_llm_execution_plan(plan_path, source_path=source_path, ir_path=ir_path)["status"] == "passed"


def test_semantic_ir_hash_ignores_random_canary_material(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(json.dumps(compile_source(source())), encoding="utf-8")
    second.write_text(json.dumps(compile_source(source())), encoding="utf-8")
    assert semantic_ir_sha256(first) == semantic_ir_sha256(second)


def test_questionless_terminal_node_is_not_an_llm_phase(tmp_path: Path) -> None:
    src = source()
    src["nodes"].append({"id": "END_DONE", "node_type": "terminal"})
    source_path, ir_path, plan_path = write_inputs(tmp_path, src)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    terminal = next(item for item in plan["phases"] if item["id"] == "END_DONE")
    assert terminal["classification"] == "terminal"
    assert validate_llm_execution_plan(plan_path, source_path=source_path, ir_path=ir_path)["status"] == "passed"


def test_stale_source_and_illegal_route_fail_closed(tmp_path: Path) -> None:
    source_path, ir_path, plan_path = write_inputs(tmp_path, source())
    source_path.write_text(source_path.read_text(encoding="utf-8") + "# changed\n", encoding="utf-8")
    report = validate_llm_execution_plan(plan_path, source_path=source_path, ir_path=ir_path)
    assert any(item["code"] == "ORDO-LLM-PLAN-STALE" for item in report["issues"])

    source_path, ir_path, plan_path = write_inputs(tmp_path, source())
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["phases"][0]["runtime_routes"] = ["MISSING_TARGET"]
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    report = validate_llm_execution_plan(plan_path, source_path=source_path, ir_path=ir_path)
    assert any(item["code"] == "ORDO-LLM-PLAN-007" for item in report["issues"])


def test_resource_cycles_and_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    src = source()
    src["resources"][0]["depends_on"] = ["R_CHILD"]
    source_path, ir_path, plan_path = write_inputs(tmp_path, src)
    report = validate_llm_execution_plan(plan_path, source_path=source_path, ir_path=ir_path)
    assert any(item["code"] == "ORDO-LLM-PLAN-RESOURCE-CYCLE" for item in report["issues"])

    source_path, ir_path, plan_path = write_inputs(tmp_path, source())
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["runtime_elements"].append({"id": "N_START", "classification": "terminal"})
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    report = validate_llm_execution_plan(plan_path, source_path=source_path, ir_path=ir_path)
    assert any(item["code"] == "ORDO-LLM-PLAN-005" for item in report["issues"])


def test_unresolved_phase_resource_fails_closed(tmp_path: Path) -> None:
    src = source()
    src["nodes"][0]["resources"] = ["R_DOES_NOT_EXIST"]
    source_path, ir_path, plan_path = write_inputs(tmp_path, src)
    report = validate_llm_execution_plan(plan_path, source_path=source_path, ir_path=ir_path)
    assert any(item["code"] == "ORDO-LLM-PLAN-RESOURCE-MISSING" for item in report["issues"])


def test_compile_cli_emits_and_runtime_rejects_stale_plan() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="ordo_bl110_cli_"))
    try:
        package = tmp / "history_event_guided_intake"
        shutil.copytree(ROOT / "packages" / "history_event_guided_intake", package)
        assert main(["compile", str(package)]) == 0
        plan = package / "compiled" / "llm_execution_plan.json"
        assert plan.exists()
        assert main(["validate-llm-plan", str(plan), "--source", str(package / "source" / "program.ordo.yaml"), "--ir", str(package / "compiled" / "program.ir.json")]) == 0
        plan_data = json.loads(plan.read_text(encoding="utf-8"))
        plan_data["compiled_from"]["canonical_yaml_sha256"] = "stale"
        plan.write_text(json.dumps(plan_data), encoding="utf-8")
        assert main(["next-step", str(package)]) == 1
        report = json.loads((package / "reports" / "next_step_report.json").read_text(encoding="utf-8"))
        assert report["runtime_status"]["status"] == "stale_plan"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
