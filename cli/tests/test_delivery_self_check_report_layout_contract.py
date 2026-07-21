from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CURRENT = {
    "reports/delivery/current/DELIVERY_GATE_REPORT.json",
    "reports/self-check/current/FINAL_PACKAGE_SELF_CHECK_REPORT.json",
    "reports/self-check/current/FINAL_PACKAGE_SELF_CHECK_REPORT.md",
}

LEGACY = {
    "SELF_CHECK_REPAIR_1_RUNTIME_CONTRACT_HYGIENE_REPORT.json",
    "SELF_CHECK_REPAIR_1_RUNTIME_CONTRACT_HYGIENE_REPORT.md",
    "SELF_CHECK_REPAIR_2_PROMPT_REGISTRY_DOCS_ALIGNMENT_REPORT.json",
    "SELF_CHECK_REPAIR_2_PROMPT_REGISTRY_DOCS_ALIGNMENT_REPORT.md",
    "SELF_CHECK_REPAIR_4_RUNTIME_PROMPT_LIMIT_TEST_ISOLATION_REPORT.json",
    "SELF_CHECK_REPAIR_4_RUNTIME_PROMPT_LIMIT_TEST_ISOLATION_REPORT.md",
    "SELF_CHECK_REPAIR_5_BOOK_ASSET_LINKS_REPORT.json",
    "SELF_CHECK_REPAIR_5_BOOK_ASSET_LINKS_REPORT.md",
    "SELF_CHECK_STEP_3_FULL_TEST_SUITE_DURATION_REPORT.json",
    "SELF_CHECK_STEP_3_FULL_TEST_SUITE_DURATION_REPORT.md",
}

def test_reports_are_not_in_repository_root() -> None:
    for name in {
        "DELIVERY_GATE_REPORT.json",
        "FINAL_PACKAGE_SELF_CHECK_REPORT.json",
        "FINAL_PACKAGE_SELF_CHECK_REPORT.md",
        *LEGACY,
    }:
        assert not (ROOT / name).exists()

def test_current_reports_exist() -> None:
    for rel in CURRENT:
        assert (ROOT / rel).is_file()

def test_legacy_reports_exist() -> None:
    base = ROOT / "reports/self-check/legacy-root"
    for name in LEGACY:
        assert (base / name).is_file()

def test_report_indexes_exist() -> None:
    assert (ROOT / "reports/delivery/README.md").is_file()
    assert (ROOT / "reports/self-check/README.md").is_file()
