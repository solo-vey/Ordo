from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEGACY_ROOT = ROOT / "docs" / "releases" / "legacy-root"
RECORDS = {
    "RELEASE_NOTES_ORDO_2026_07_14_RC1.md": "5a58448b84c82f0e1a8e98a8db3c0c09ffa9fe678b55679a810ce1b00b84ca5a",
    "RELEASE_NOTES_ORDO_2026_07_14_RC3.md": "a440e57279b2707e39ce7205ef59efaf9bd970f70428ae5ffcf6b21769184da2",
}


def test_legacy_release_notes_are_absent_from_repository_root() -> None:
    assert not [name for name in RECORDS if (ROOT / name).exists()]


def test_legacy_release_notes_are_preserved_byte_for_byte() -> None:
    for name, expected_sha256 in RECORDS.items():
        path = LEGACY_ROOT / name
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha256


def test_release_notes_index_links_every_relocated_document() -> None:
    index = (LEGACY_ROOT / "README.md").read_text(encoding="utf-8")
    for name in RECORDS:
        assert f"]({name})" in index


def test_legacy_index_marks_release_notes_as_historical() -> None:
    index = (LEGACY_ROOT / "README.md").read_text(encoding="utf-8")
    assert "historical RC1 and RC3 states" in index
    assert "must not be interpreted as the current release identity" in index
