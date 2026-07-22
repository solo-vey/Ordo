from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOCATOR = ROOT / "manifests/external_archives/HISTORICAL_PROVENANCE_2026_07_22.json"


def test_legacy_release_notes_are_absent_from_active_tree() -> None:
    assert not (ROOT / "docs/releases/legacy-root").exists()


def test_legacy_release_notes_have_a_checksum_bound_external_location() -> None:
    locator = json.loads(LOCATOR.read_text(encoding="utf-8"))
    assert "docs/releases/legacy-root/" in locator["included_contours"]
    assert locator["archive"]["sha256"] == "265ce7ad9bca1ca285615a7c434bc0689ee87ff37b3cb77852fd7f4b43affc0d"
