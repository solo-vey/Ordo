from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import yaml

from ordo.compiler import compile_source
from ordo.linter import lint_source


ROOT = Path(__file__).resolve().parents[2]


def gate_source() -> dict:
    return {
        "program": {"id": "gate.contract", "version": "0.1.0"},
        "nodes": [],
        "gates": [
            {
                "id": "G_READY",
                "method": "mechanical",
                "trust_class": "deterministic",
                "condition": "state.ready is not null",
                "on_pass": "STOP",
                "on_fail": "STOP",
            }
        ],
    }


def test_gate_schema_declares_condition_as_the_canonical_field() -> None:
    schema = yaml.safe_load((ROOT / "language" / "schemas" / "gate_schema.yaml").read_text(encoding="utf-8"))
    gate = schema["Gate"]
    assert "condition" in gate["required"]
    assert "assert" not in gate["required"]
    assert "condition" in gate["properties"]
    assert "assert" not in gate["properties"]


def test_compiler_preserves_the_canonical_gate_condition() -> None:
    compiled = compile_source(deepcopy(gate_source()))
    gate = next(op for op in compiled["ops"] if op["op"] == "GATE.DEF")
    assert gate["condition"] == "state.ready is not null"
    assert "assert" not in gate


def test_linter_rejects_legacy_gate_assert_field() -> None:
    source = gate_source()
    source["gates"][0]["assert"] = source["gates"][0].pop("condition")
    report = lint_source(source, {"test_cases": [{}]})
    codes = {issue["code"] for issue in report["issues"]}
    assert "GATE_LEGACY_ASSERT_FIELD" in codes
    assert "GATE_CONDITION_REQUIRED" in codes
