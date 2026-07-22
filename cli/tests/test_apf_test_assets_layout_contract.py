from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_apf_test_assets_are_consolidated_under_cli_tests() -> None:
    assert not (ROOT / "fixtures").exists()
    assert not (ROOT / "tests").exists()
    assert (ROOT / "cli/tests/fixtures/apf_real_case_replay/history_event_replay_cases.json").is_file()


def test_legacy_apf_tests_are_in_the_cli_test_suite() -> None:
    expected = {
        "test_m74_5_apf_semantic_equivalence.py",
        "test_m74_6_apf_modular_assembly.py",
        "test_m77_5_real_apf_flow_reuse_equivalence.py",
    }
    actual = {path.name for path in (ROOT / "cli/tests").glob("test_*apf*.py")}
    assert expected <= actual
