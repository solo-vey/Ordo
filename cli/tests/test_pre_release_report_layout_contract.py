from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEGACY_ROOT = ROOT / "reports" / "pre-release" / "legacy-root"
RECORDS = (
    "PRE_RELEASE_HISTORY_EVENT_CLEAN_CHECK.json",
    "PRE_RELEASE_REPO_CHECK.json",
    "PRE_RELEASE_STATUS.json",
    "PRE_RELEASE_STATUS.md",
)


def test_pre_release_records_are_absent_from_repository_root() -> None:
    assert not [name for name in RECORDS if (ROOT / name).exists()]


def test_pre_release_records_are_preserved_under_legacy_root() -> None:
    assert not [name for name in RECORDS if not (LEGACY_ROOT / name).is_file()]


def test_pre_release_json_records_remain_parseable() -> None:
    for name in RECORDS:
        if name.endswith(".json"):
            parsed = json.loads((LEGACY_ROOT / name).read_text(encoding="utf-8"))
            assert isinstance(parsed, dict)


def test_legacy_index_marks_records_as_historical() -> None:
    index = (LEGACY_ROOT / "README.md").read_text(encoding="utf-8")
    assert "historical evidence" in index
    assert "rather than current project claims" in index
