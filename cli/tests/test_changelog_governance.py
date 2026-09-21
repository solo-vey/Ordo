from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_changelog_tracks_current_vibe_and_editor_releases() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    vibe = json.loads((ROOT / "manifests/VIBE_ARF_CURRENT.json").read_text(encoding="utf-8"))
    editor = json.loads(
        (ROOT / "utilities/ordo_tree_editor/web/api-docs/openapi.json").read_text(encoding="utf-8")
    )

    assert changelog.startswith("# Changelog\n")
    assert "## [Unreleased]" in changelog
    assert f"## [Vibe ARF {vibe['version']}]" in changelog
    assert f"## [Ordo Tree Editor {editor['info']['version']}]" in changelog
    assert "## Changelog maintenance" in changelog
