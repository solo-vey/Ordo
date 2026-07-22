from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOCATOR = ROOT / "manifests/external_archives/HISTORICAL_PROVENANCE_2026_07_22.json"
CHECKSUMS = ROOT / "SHA256SUMS.txt"
ARCHIVED_CONTOURS = (
    "TRANSFER_2026-07-14",
    "recovery/2026-07-14",
    "archive/handoffs",
    "docs/handoff/legacy-root",
    "docs/releases/legacy-root",
    "docs/status/legacy-root",
    "manifests/releases/legacy-root",
    "checkpoints",
)


def checksum_entries() -> dict[str, str]:
    return {
        path: digest
        for digest, path in (line.split("  ", 1) for line in CHECKSUMS.read_text(encoding="utf-8").splitlines())
    }


def test_external_archive_locator_is_checksum_bound() -> None:
    locator = json.loads(LOCATOR.read_text(encoding="utf-8"))
    assert locator["schema_version"] == "ordo.external_archive_locator.v1"
    assert locator["archive_id"] == "historical-provenance-2026-07-22"
    assert locator["provider"] == "github_release_asset"
    assert locator["included_contours"] == [f"{path}/" for path in ARCHIVED_CONTOURS]
    assert locator["excluded_contours"] == ["docs/apf/legacy-root/"]
    for key in ("archive", "content_manifest", "content_checksums"):
        assert locator[key]["asset_url"].startswith("https://github.com/solo-vey/Ordo/releases/download/")
        assert len(locator[key]["sha256"]) == 64


def test_archived_contours_are_absent_from_active_tree_and_checksums() -> None:
    checksums = checksum_entries()
    for contour in ARCHIVED_CONTOURS:
        assert not (ROOT / contour).exists(), contour
        assert not any(path.startswith(f"{contour}/") for path in checksums), contour


def test_locator_and_documentation_are_current_repository_artifacts() -> None:
    checksums = checksum_entries()
    for path in ("manifests/external_archives/HISTORICAL_PROVENANCE_2026_07_22.json", "docs/EXTERNAL_ARCHIVES.md"):
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == checksums[path]
