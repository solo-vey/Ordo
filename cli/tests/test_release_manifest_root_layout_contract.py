from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOCATOR = ROOT / "manifests/external_archives/HISTORICAL_PROVENANCE_2026_07_22.json"


def test_legacy_release_manifests_are_absent_from_active_tree() -> None:
    assert not (ROOT / "manifests/releases/legacy-root").exists()


def test_legacy_release_manifests_have_a_checksum_bound_external_location() -> None:
    locator = json.loads(LOCATOR.read_text(encoding="utf-8"))
    assert "manifests/releases/legacy-root/" in locator["included_contours"]
    assert locator["content_manifest"]["sha256"] == "47e0ad5559330a8e8d85a453ed374d528a405b429ed08c3778556e7c0ecf64c6"
