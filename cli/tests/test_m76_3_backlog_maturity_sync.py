import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_issue_tracking_replaces_historical_backlog_sync():
    tracking = json.loads((ROOT / "manifests/ISSUE_TRACKING.json").read_text(encoding="utf-8"))
    assert tracking["canonical_tracker"] == "https://github.com/solo-vey/Ordo/issues"
    assert tracking["historical_backlog_branch"] == "archive/legacy"
    assert tracking["active_issues"]


def test_current_csg_maturity_is_production_ready_everywhere():
    manifest = json.loads((ROOT / "manifests/CSG_RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["capability"] == "conversation_scope_guard"

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
    ledger = json.loads((ROOT / "manifests/RELEASE_LEDGER.json").read_text(encoding="utf-8"))
    completed = {
        item
        for release in ledger["releases"]
        for item in release.get("completed_backlog_items", [])
    }
    assert "BL-ORDO-004" in completed
