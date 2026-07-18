from pathlib import Path

from ordo.prompt_registry_reconcile import reconcile_prompt_registry

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "packages" / "history_event_guided_intake"


def test_real_registry_reconciliation_passes() -> None:
    report = reconcile_prompt_registry(PKG)
    assert report["status"] == "passed"
    assert report["registry_entries"] == 13
    assert report["manifest_entries"] == 13
    assert report["orphaned_prompt_ids"] == []
    assert report["conditional_dormant_prompt_ids"] == ["hp.repair.backtracking_invalidation.v1"]


def test_startup_prompts_count_as_runtime_attachments() -> None:
    report = reconcile_prompt_registry(PKG)
    assert report["attachments"]["hp.package.quick_start.v1"][0]["channel"] == "startup_mode"
    assert report["attachments"]["hp.runtime.start.v1"][0]["channel"] == "startup_mode"


def test_non_prompt_versioned_ids_are_not_misclassified() -> None:
    report = reconcile_prompt_registry(PKG)
    all_prompt_ids = set(report["active_prompt_ids"]) | set(report["conditional_dormant_prompt_ids"])
    assert "ordo.clean_check.report.v1" not in all_prompt_ids
    assert "ordo.prompt_application_trace.v1" not in all_prompt_ids


def test_registry_and_manifest_checksums_are_aligned() -> None:
    report = reconcile_prompt_registry(PKG)
    assert report["missing_manifest_entries"] == []
    assert report["extra_manifest_entries"] == []
    assert report["missing_prompt_files"] == []
    assert report["checksum_mismatches"] == []
