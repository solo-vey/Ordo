from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_issue_tracking_is_the_active_planning_contract() -> None:
    tracker = json.loads((ROOT / "manifests/ISSUE_TRACKING.json").read_text(encoding="utf-8"))
    document = (ROOT / "docs/PROJECT_TRACKING.md").read_text(encoding="utf-8")
    assert tracker["schema_version"] == "ordo.issue_tracking.v1"
    assert tracker["canonical_tracker"] == "https://github.com/solo-vey/Ordo/issues"
    assert tracker["historical_backlog_branch"] == "archive/legacy"
    assert {item["id"] for item in tracker["active_issues"]} == {"BL-ORDO-026", "BL-ORDO-043", "BL-ORDO-062"}
    for item in tracker["active_issues"]:
        assert item["url"] in document
        assert f"#{item['issue']}" in document
