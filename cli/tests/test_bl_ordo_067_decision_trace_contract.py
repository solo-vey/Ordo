from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "contracts" / "BL_ORDO_067_DECISION_TRACE_CONTRACT.yaml"


def load_contract() -> dict:
    return yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))


def test_contract_captures_observable_facts_and_hypothesis_boundary() -> None:
    contract = load_contract()
    assert contract["status"] == "design_only"
    assert contract["runtime_semantics_changed"] is False
    assert "rendered_message" in contract["required_observable_facts"]
    assert "analyst_response" in contract["required_observable_facts"]
    assert "decision_summary" in contract["required_hypothesis"]
    assert "chain_of_thought" in contract["redaction"]["forbidden_fields"]
    assert "raw_system_prompt" in contract["redaction"]["forbidden_fields"]


def test_contract_defines_replay_anchor_and_capture_levels() -> None:
    contract = load_contract()
    assert {"off", "standard", "diagnostic"} <= set(contract["capture_levels"])
    required = set(contract["replay_anchor"]["required"])
    assert {"ir_hash", "source_digest", "node_id", "step_index", "model_identity"} <= required


def test_contract_example_does_not_persist_hidden_reasoning() -> None:
    contract = load_contract()
    example_text = repr(contract["example"]).lower()
    assert "chain_of_thought" not in example_text
    assert "private_reasoning" not in example_text
    assert contract["example"]["decision_summary"]["classification"] == "hypothesis"
