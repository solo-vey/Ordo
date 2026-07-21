import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def _md_statuses(text: str):
    return dict(re.findall(r"### (BL-ORDO-\d+) — .*?\n\nStatus: `([^`]+)`", text, re.S))


def test_consolidated_backlog_md_json_statuses_match():
    md = _md_statuses((ROOT / "backlog/CONSOLIDATED_BACKLOG.md").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "manifests/CONSOLIDATED_BACKLOG.json").read_text(encoding="utf-8"))
    js = {item["id"]: item["status"] for item in data["items"]}
    assert md == js


def test_current_csg_maturity_is_production_ready_everywhere():
    current = json.loads((ROOT / "manifests/CURRENT_MATURITY_STATE.json").read_text(encoding="utf-8"))
    csg = current["capabilities"]["conversation_scope_guard"]
    assert csg["production_recommendation"] == "ready"
    assert csg["runtime_enforcement"] == "integrated_helper_runner"
    assert csg["model_benchmark"] == "passed_cross_model_repeated_runs"

    contract = (ROOT / "language/CONVERSATION_SCOPE_GUARD_CONTRACT.md").read_text(encoding="utf-8")
    integration = (ROOT / "language/CSG_INTEGRATION_LINE.md").read_text(encoding="utf-8")
    for text in (contract, integration):
        assert "production_recommendation: ready" in text
        assert "runtime_enforcement: integrated_helper_runner" in text
        assert "model_benchmark: passed_cross_model_repeated_runs" in text


def test_historical_stale_statuses_are_registered_as_superseded():
    registry = json.loads((ROOT / "manifests/STATUS_SUPERSESSION_REGISTRY.json").read_text(encoding="utf-8"))
    registered = {r["path"] for r in registry["records"]}
    required = {
        "reports/M74_0_CSG_MATURITY_REASSESSMENT.json",
        "M74_3_VALIDATION_REPORT.json",
        "M74_3_REAL_MODEL_BENCHMARK_CLOSURE_REPORT.json",
        "manifests/LANGUAGE_BASELINE_RELEASE_CSG_0_1.json",
        "manifests/M74_1_LANGUAGE_BASELINE_DELTA.json",
    }
    assert required <= registered
    assert all(r["preserve_unchanged"] is True for r in registry["records"])


def test_bl_ordo_004_is_closed_with_evidence():
    data = json.loads((ROOT / "manifests/CONSOLIDATED_BACKLOG.json").read_text(encoding="utf-8"))
    item = next(i for i in data["items"] if i["id"] == "BL-ORDO-004")
    assert item["status"] == "closed"
    assert item["closure_milestone"] == "M76.3"
    assert (ROOT / item["closure_evidence"]).exists()
