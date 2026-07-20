from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

MOVED = {
    "APF_COMPANION_WORKFLOW.md",
    "APF_DOCUMENTATION_AND_BOOK_SECTION.md",
    "APF_INTEGRATION_CORRELATION_PLAN.md",
    "APF_LANGUAGE_PATTERN_CANDIDATES.md",
    "APF_LANGUAGE_PATTERN_EXTRACTION_PLAN.md",
    "APF_PACKAGE_IMPORT.md",
    "APF_PATTERN_CLASSIFICATION_MATRIX.md",
    "APF_RC_PATTERN_CLASSIFICATION.md",
    "APF_RC_STANDARD_MODULE_STATUS.md",
    "APF_SESSION_PACKAGE_LOAD_AND_CACHE_BACKLOG.md",
    "APF_STANDARD_MODULE_GUIDE.md",
    "COMPANION_UTILITIES.md",
    "COMPANION_UTILITY_WORKFLOW.md",
    "STANDARD_APPLIED_MODULES.md",
}


def test_apf_legacy_documents_are_not_in_repository_root() -> None:
    for name in MOVED:
        assert not (ROOT / name).exists()


def test_apf_legacy_documents_are_preserved_under_docs() -> None:
    destination = ROOT / "docs/apf/legacy-root"
    assert (destination / "README.md").is_file()
    for name in MOVED:
        assert (destination / name).is_file()


def test_apf_legacy_index_links_every_relocated_document() -> None:
    text = (ROOT / "docs/apf/legacy-root/README.md").read_text(encoding="utf-8")
    for name in MOVED:
        assert f"]({name})" in text


def test_localized_apf_rationale_is_deferred() -> None:
    assert (ROOT / "APF_POST_GENERATION_DEFECT_REVIEW_RATIONALE_UK.md").is_file()
