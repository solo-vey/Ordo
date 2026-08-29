from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
PRH = ROOT / "utilities" / "playbook_regression_harness" / "versions" / "1.7.0"
PRP = ROOT / "packages" / "playbook_regression" / "versions" / "0.2.0-alpha.1"
ARF_REGRESSION = ROOT / "archive" / "legacy_packages" / "arf_playbook_kit" / "source" / "regression"


def _files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file()]


def test_prh_and_prp_versions_and_dependency_are_explicit() -> None:
    assert (PRH / "README.md").exists()
    assert (PRH / "CHANGELOG_1.7.0.md").exists()
    manifest = yaml.safe_load((PRP / "playbook_manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.2.0-alpha.1"
    dependency = manifest["embedded_modules"][0]
    assert dependency["version"] == "1.7.0"
    assert dependency["path"] == "embedded_modules/PLAYBOOK_REGRESSION_HARNESS_1.7.0/"
    assert dependency["source_of_truth"].endswith("utilities/playbook_regression_harness/versions/1.7.0/")


def test_integrated_contours_are_expanded_english_source_without_zip_binaries() -> None:
    for root in (PRH, PRP, ARF_REGRESSION):
        assert not list(root.rglob("*.zip"))
        assert not [path for path in _files(root) if path.name.endswith("_UA.md")]

    assert (PRH / "prompts" / "PROMPT_RUN_UNIFIED_PRH_FROM_START.md").exists()
    assert (PRP / "prompts" / "START_PRP.md").exists()
    assert (ARF_REGRESSION / "prh" / "1.7.0").exists()
    assert (ARF_REGRESSION / "prp" / "0.2.0-alpha.1").exists()


def test_prp_release_remains_candidate() -> None:
    release = json.loads((PRP / "playbook_release.json").read_text(encoding="utf-8"))
    assert release["release_status"] == "candidate"
    assert release["canonical_claim"] is False
