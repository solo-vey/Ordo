from pathlib import Path

from ordo.cli import main
from ordo.template_tooling import validate_template_contract

ROOT = Path(__file__).resolve().parents[2]


def test_valid_model_rendered_template_contract_passes(tmp_path):
    src = ROOT / "examples" / "template_tooling" / "qa_package.template.yaml"
    report = validate_template_contract(src)
    assert report["status"] == "passed"
    assert report["render_mode"] == "model_rendered"
    assert report["sha256"]


def test_missing_model_contract_fails(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text(
        """template_id: qa.bad\nversion: 1.0.0\nrender_mode: model_rendered\ninput_schema: {}\noutput_contract: {}\nreview_profile: strict\ncompatibility: {}\n""",
        encoding="utf-8",
    )
    report = validate_template_contract(p)
    assert report["status"] == "failed"
    assert any(i["code"] == "TEMPLATE_MODEL_CONTRACT_REQUIRED" for i in report["issues"])


def test_cli_template_validate_writes_report(tmp_path):
    src = ROOT / "examples" / "template_tooling" / "qa_package.template.yaml"
    out = tmp_path / "report.json"
    rc = main(["template", "validate", str(src), "--out", str(out)])
    assert rc == 0
    assert out.exists()


def test_docs_and_book_are_updated():
    assert (ROOT / "docs" / "GENERIC_TEMPLATE_TOOLING.md").exists()
    book = (ROOT / "book" / "uk" / "chapters" / "appendix_f_praktychnyi_dovidnyk_opkodiv_i_yaml_atrybutiv.md").read_text(encoding="utf-8")
    assert "ordo template" in book
    assert "model_rendered" in book
