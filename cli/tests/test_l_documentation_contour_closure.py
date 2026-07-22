from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLOSURE_PATH = ROOT / "manifests/L_DOCUMENTATION_CONTOUR_CLOSURE.json"


def load_json(path: str | Path) -> dict:
    target = path if isinstance(path, Path) else ROOT / path
    return json.loads(target.read_text(encoding="utf-8"))


def test_l_closure_records_all_phases_and_merged_evidence() -> None:
    closure = load_json(CLOSURE_PATH)
    phases = closure["phases"]

    assert closure["schema_version"] == "ordo.documentation_contour_closure.v1"
    assert closure["contour_id"] == "L"
    assert closure["status"] == "closed"
    assert closure["validated_main_baseline"] == "f42a89112610ec22defc35d3a20c88fa087c0c74"
    assert [phase["id"] for phase in phases] == ["L.1", "L.2", "L.3", "L.4"]
    assert all(phase["status"] == "closed" for phase in phases)
    assert [phase["pull_request"] for phase in phases[1:]] == [20, 21, 22]


def test_l_status_is_synchronized_across_current_state_records() -> None:
    closure = load_json(CLOSURE_PATH)
    backlog = load_json("manifests/CONSOLIDATED_BACKLOG.json")
    maturity = load_json("manifests/CURRENT_MATURITY_STATE.json")
    backlog_md = (ROOT / "backlog/CONSOLIDATED_BACKLOG.md").read_text(encoding="utf-8")
    maturity_md = (ROOT / "backlog/CURRENT_MATURITY_STATE.md").read_text(encoding="utf-8")

    contour = next(item for item in backlog["maintenance_contours"] if item["id"] == "L")
    assert contour["status"] == "closed"
    assert contour["closure_evidence"] == CLOSURE_PATH.relative_to(ROOT).as_posix()
    assert backlog["next_documentation_tasks"] == []
    assert maturity["documentation_quality"]["status"] == "closed"
    assert maturity["documentation_quality"]["closure_evidence"] == contour["closure_evidence"]
    assert maturity["next_documentation_tasks"] == []
    assert "### L — Documentation quality and chat-first onboarding\n\nStatus: `closed`" in backlog_md
    assert "Documentation contour L: `closed`" in maturity_md
    assert closure["next_documentation_tasks"] == []


def test_l_closure_keeps_evidence_discoverable_and_debt_bounded() -> None:
    closure = load_json(CLOSURE_PATH)
    policy = load_json("manifests/DOCUMENTATION_QUALITY_GATE.json")

    assert all((ROOT / path).is_file() for path in closure["canonical_deliverables"])
    assert all((ROOT / path).is_file() for path in closure["out_of_scope_preserved_debt"])
    assert not set(closure["out_of_scope_preserved_debt"]) & set(policy["active_documents"])
    assert "docs/status/L_DOCUMENTATION_CONTOUR_CLOSURE.md" in policy["active_documents"]
    assert closure["historical_contours_rewritten"] is False


def test_l_closure_records_green_ci_and_reproducible_final_archive() -> None:
    closure = load_json(CLOSURE_PATH)
    final_archive = closure["final_archive"]

    assert {item["status"] for item in closure["post_merge_ci"]} == {"success"}
    assert {item["workflow"] for item in closure["post_merge_ci"]} == {
        "clean-gate",
        "ordo-checks",
        "full-delivery-gate",
    }
    assert final_archive == {
        "type": "reproducible_release_candidate",
        "builder": "tools/build_release_archive.py",
        "validated_from_main_baseline": "f42a89112610ec22defc35d3a20c88fa087c0c74",
        "status": "passed",
        "repository_copy": "not_persisted_generated_output",
    }
