from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RELOCATIONS = {
    "CONSOLIDATED_BACKLOG.md": "backlog/CONSOLIDATED_BACKLOG.md",
    "CURRENT_MATURITY_STATE.md": "backlog/CURRENT_MATURITY_STATE.md",
    "FUTURE_BACKLOG.md": "backlog/FUTURE_BACKLOG.md",
    "DELIVERY_POLICY.md": "docs/policies/DELIVERY_POLICY.md",
    "LANGUAGE_POLICY.md": "docs/policies/LANGUAGE_POLICY.md",
    "PLAYBOOK_VERSIONING_POLICY.md": "docs/policies/PLAYBOOK_VERSIONING_POLICY.md",
    "README_LICENSE_SECTION.md": "docs/policies/README_LICENSE_SECTION.md",
    "RELEASE_INTEGRITY_POLICY.md": "docs/policies/RELEASE_INTEGRITY_POLICY.md",
    "TEST_FIXTURE_AND_PARALLEL_SAFETY_POLICY.md": "docs/policies/TEST_FIXTURE_AND_PARALLEL_SAFETY_POLICY.md",
    "VERSIONING_POLICY.md": "docs/policies/VERSIONING_POLICY.md",
    "DEVELOPER_BUNDLE_README.md": "docs/handoff/DEVELOPER_BUNDLE_README.md",
    "STABLE_DEVELOPER_HANDOFF.md": "docs/handoff/legacy-root/STABLE_DEVELOPER_HANDOFF.md",
    "START_PROMPT_DEVELOPER_MODE.md": "docs/handoff/START_PROMPT_DEVELOPER_MODE.md",
    "README_CURRENT_HANDOFF_UK.md": "archive/handoffs/legacy-root/README_CURRENT_HANDOFF_UK.md",
    "README_CURRENT_PACKAGE_UK.md": "archive/handoffs/legacy-root/README_CURRENT_PACKAGE_UK.md",
}
LOCALIZED_HASHES = {
    "README_CURRENT_HANDOFF_UK.md": "44a87b981c2f5b81cdb1e013ccce0ccf681560634be38cb2c348f77f4f692403",
    "README_CURRENT_PACKAGE_UK.md": "6892a864d31d7f05ac5ccaced36eeb1c2a78ea45b768f0b7a552d64342ecd457",
}


def test_governance_documents_are_absent_from_repository_root() -> None:
    assert not [name for name in RELOCATIONS if (ROOT / name).exists()]


def test_governance_documents_exist_in_canonical_contours() -> None:
    assert not [target for target in RELOCATIONS.values() if not (ROOT / target).is_file()]


def test_localized_handoffs_are_preserved_byte_for_byte() -> None:
    for name, expected_sha256 in LOCALIZED_HASHES.items():
        target = ROOT / RELOCATIONS[name]
        assert hashlib.sha256(target.read_bytes()).hexdigest() == expected_sha256


def test_indexes_explain_current_and_historical_ownership() -> None:
    backlog = (ROOT / "backlog/README.md").read_text(encoding="utf-8")
    policies = (ROOT / "docs/policies/README.md").read_text(encoding="utf-8")
    handoffs = (ROOT / "docs/handoff/README.md").read_text(encoding="utf-8")
    archive = (ROOT / "archive/handoffs/legacy-root/README.md").read_text(encoding="utf-8")
    assert "canonical Markdown backlog" in backlog
    assert "normative and reusable repository policy" in policies
    assert "developer-mode start prompt" in handoffs
    assert "not the present repository state" in archive


def test_tooling_uses_relocated_canonical_paths() -> None:
    builder = (ROOT / "tools/build_release_archive.py").read_text(encoding="utf-8")
    profile = (ROOT / "language/STARTUP_PACKAGE_PROFILE.md").read_text(encoding="utf-8")
    assert 'ROOT / "backlog/CONSOLIDATED_BACKLOG.md"' in builder
    assert "entry_file: docs/handoff/START_PROMPT_DEVELOPER_MODE.md" in profile
