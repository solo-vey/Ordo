
from pathlib import Path
import json
from utilities.ordo_tree_editor.verification import runner

def test_source_only_state_and_journey_are_skipped(tmp_path):
    state=json.loads((runner.CHECKS_DIR/"100_validate_state.json").read_text())
    journey=json.loads((runner.CHECKS_DIR/"110_validate_journey.json").read_text())
    ok,reason=runner._applicable(state,tmp_path,None)
    assert not ok and "not applicable" in reason.lower()
    ok,reason=runner._applicable(journey,tmp_path,None)
    assert not ok and "journey" in reason.lower()

def test_runtime_evidence_makes_state_applicable(tmp_path):
    p=tmp_path/"runtime/live_session_state.json"; p.parent.mkdir(parents=True); p.write_text('{"state":{}}')
    state=json.loads((runner.CHECKS_DIR/"100_validate_state.json").read_text())
    ok,_=runner._applicable(state,tmp_path,None)
    assert ok

def test_empty_journey_yaml_does_not_make_check_applicable(tmp_path):
    p=tmp_path/"runtime/MANUAL_RUN_JOURNEY.yaml"; p.parent.mkdir(parents=True); p.write_text("events: []\n")
    journey=json.loads((runner.CHECKS_DIR/"110_validate_journey.json").read_text())
    ok,_=runner._applicable(journey,tmp_path,None)
    assert not ok

def test_generated_report_evidence_is_embedded(tmp_path):
    reports=tmp_path/"reports"; reports.mkdir()
    before=runner._report_snapshot(tmp_path)
    report=reports/"release_provenance_validation_report.json"
    report.write_text(json.dumps({"status":"failed","errors":[{"code":"PROVENANCE_MISSING","message":"manifest missing"}]}))
    evidence=runner._collect_generated_evidence(tmp_path,before,str(report))
    assert evidence and evidence[0]["content_json"]["errors"][0]["code"]=="PROVENANCE_MISSING"
    summary=runner._evidence_summary(evidence)
    assert "PROVENANCE_MISSING" in summary
