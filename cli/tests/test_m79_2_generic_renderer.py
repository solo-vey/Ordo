from pathlib import Path
import json
import yaml

from ordo.cli import main
from ordo.template_tooling import render_template

ROOT = Path(__file__).resolve().parents[2]
EX = ROOT / "examples" / "template_tooling"


def test_deterministic_renderer_creates_artifact_and_evidence(tmp_path):
    report = render_template(EX / "deterministic_summary.template.yaml", EX / "render_input.yaml", tmp_path)
    assert report["status"] == "passed", report
    assert report["mode"] == "deterministic"
    assert (tmp_path / "summary.md").read_text().startswith("# Release summary")
    assert (tmp_path / "render_evidence.json").exists()


def test_model_rendered_creates_controlled_job(tmp_path):
    report = render_template(EX / "qa_package.template.yaml", EX / "render_input.yaml", tmp_path)
    assert report["status"] == "failed"  # input schema mismatch is enforced
    input_path = tmp_path / "qa_input.yaml"
    input_path.write_text("scope: release\nfindings: []\n", encoding="utf-8")
    report = render_template(EX / "qa_package.template.yaml", input_path, tmp_path)
    assert report["status"] == "passed", report
    job = json.loads((tmp_path / "model_render_job.json").read_text())
    assert job["schema_version"] == "ordo.template.render_job.v1"
    assert job["prompt_ref"] == "prompt.qa.package.render.v1"


def test_hybrid_creates_scaffold_and_job(tmp_path):
    contract = yaml.safe_load((EX / "deterministic_summary.template.yaml").read_text())
    contract["template_id"] = "summary.hybrid"
    contract["render_mode"] = "hybrid"
    contract["model_contract"] = {"prompt_ref": "prompt.summary.complete.v1", "provenance_required": True}
    p = tmp_path / "hybrid.yaml"
    p.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
    (tmp_path / "deterministic_summary.md.tmpl").write_text((EX / "deterministic_summary.md.tmpl").read_text(), encoding="utf-8")
    report = render_template(p, EX / "render_input.yaml", tmp_path / "out")
    assert report["status"] == "passed", report
    assert (tmp_path / "out" / "summary.md").exists()
    assert (tmp_path / "out" / "model_render_job.json").exists()


def test_cli_template_render(tmp_path):
    rc = main(["template", "render", str(EX / "deterministic_summary.template.yaml"), "--input", str(EX / "render_input.yaml"), "--output-dir", str(tmp_path)])
    assert rc == 0
    assert (tmp_path / "render_report.json").exists()
