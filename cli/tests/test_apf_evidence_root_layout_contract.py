from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

MOVED = {
    "APF_PATTERN_CLASSIFICATION_MATRIX.csv",
    "APF_PATTERN_CLASSIFICATION_MATRIX.json",
    "APF_RC_PATTERN_CLASSIFICATION.csv",
}


def test_apf_evidence_is_not_in_repository_root() -> None:
    for name in MOVED:
        assert not (ROOT / name).exists()


def test_apf_evidence_is_preserved_under_reports() -> None:
    destination = ROOT / "reports/apf/legacy-root"
    assert (destination / "README.md").is_file()
    for name in MOVED:
        assert (destination / name).is_file()


def test_apf_evidence_index_links_all_artifacts() -> None:
    text = (ROOT / "reports/apf/legacy-root/README.md").read_text(encoding="utf-8")
    for name in MOVED:
        assert f"]({name})" in text
