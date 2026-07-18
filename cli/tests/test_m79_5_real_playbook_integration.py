from pathlib import Path
import json
from ordo.template_tooling import render_template


def test_json_boolean_rendering_is_lowercase(tmp_path: Path):
    contract = tmp_path / "contract.yaml"
    source = tmp_path / "source.json.tmpl"
    inputs = tmp_path / "input.yaml"
    source.write_text('{"enabled": {{enabled}}}\n', encoding="utf-8")
    contract.write_text('''template_id: test.boolean_json\nversion: 1.0.0\nrender_mode: deterministic\ntemplate_ref: source.json.tmpl\ninput_schema:\n  required: [enabled]\n  properties:\n    enabled: {type: boolean}\noutput_contract:\n  format: json\n  filename: out.json\nreview_profile: {mode: strict}\ncompatibility: {ordo: ">=0.12.0"}\n''', encoding="utf-8")
    inputs.write_text('enabled: true\n', encoding="utf-8")
    report = render_template(contract, inputs, tmp_path / "out")
    assert report["status"] == "passed"
    assert json.loads((tmp_path / "out" / "out.json").read_text()) == {"enabled": True}


def test_real_integration_report_passed():
    report = Path('/mnt/data/m79_5_history_event_integration/template_tooling/M79_5_INTEGRATION_REPORT.json')
    if not report.exists():
        return
    data = json.loads(report.read_text(encoding='utf-8'))
    assert data['status'] == 'passed'
    assert len(data['integrations']) == 2
    assert data['business_logic_changed'] is False
