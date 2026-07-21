from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEGACY_ROOT = ROOT / "manifests" / "releases" / "legacy-root"
RECORDS = {
    "CHANGE_BUNDLE_MANIFEST.json": "5cc831c424a15917b36b8634d108cd8427b62833c8d06a96883458f2dc510c5a",
    "RELEASE_MANIFEST_M83_0.json": "883c3310a8ff1273d015e2efa24d7074cfaf3117ce471080a1e285c6dfd4deb5",
}


def test_legacy_release_manifests_are_absent_from_repository_root() -> None:
    assert not [name for name in RECORDS if (ROOT / name).exists()]


def test_legacy_release_manifests_are_preserved_byte_for_byte() -> None:
    for name, expected_sha256 in RECORDS.items():
        path = LEGACY_ROOT / name
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha256


def test_legacy_release_manifests_remain_parseable() -> None:
    change_bundle = json.loads((LEGACY_ROOT / "CHANGE_BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))
    release = json.loads((LEGACY_ROOT / "RELEASE_MANIFEST_M83_0.json").read_text(encoding="utf-8"))
    assert change_bundle["canonical_release_created"] is False
    assert release["release_label"] == "M83.0"


def test_legacy_index_marks_manifests_as_historical() -> None:
    index = (LEGACY_ROOT / "README.md").read_text(encoding="utf-8")
    assert "historical RC9 and M83.0 transition states" in index
    assert "must not be interpreted as the current release identity" in index
