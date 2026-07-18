from pathlib import Path
import json
import tempfile
import yaml
from ordo.manual_run_journey import append_journey_event, record_intake_event, validate_journey, finalize_journey


def test_append_only_chain_and_consolidated_view(tmp_path: Path):
    append_journey_event(tmp_path, run_id="R1", event_type="system_action", payload={"status":"completed"})
    finalize_journey(tmp_path, run_id="R1", status="completed", node_id="T_DONE")
    lines=(tmp_path/"runtime/manual_run_journey.events.jsonl").read_text().splitlines()
    assert len(lines)==2
    doc=yaml.safe_load((tmp_path/"runtime/MANUAL_RUN_JOURNEY.yaml").read_text())
    assert doc["run"]["status"]=="completed"
    assert validate_journey(tmp_path)["status"]=="passed"


def test_rejected_answer_does_not_record_state_change(tmp_path: Path):
    record_intake_event(tmp_path, run_id="R2", node={"id":"N1","question":"Name?","question_id":"Q_NAME"},
        answer="", status="blocked", state_before={}, state_after={}, state_diff={}, next_node=None,
        issues=[{"code":"invalid"}], trace={"step_index":1,"digest":"sha256:x"}, snapshot_path="s", snapshot_hash="h")
    doc=yaml.safe_load((tmp_path/"runtime/MANUAL_RUN_JOURNEY.yaml").read_text())
    event=doc["events"][0]
    assert event["answer_status"]=="rejected"
    assert event["state_change"]["changed_fields"]=={}
    assert validate_journey(tmp_path)["status"]=="passed"


def test_validator_detects_event_tampering(tmp_path: Path):
    append_journey_event(tmp_path, run_id="R3", event_type="system_action", payload={"status":"completed"})
    p=tmp_path/"runtime/MANUAL_RUN_JOURNEY.yaml"
    doc=yaml.safe_load(p.read_text()); doc["events"][0]["status"]="tampered"; p.write_text(yaml.safe_dump(doc,sort_keys=False))
    report=validate_journey(tmp_path)
    assert report["status"]=="failed"
    assert any(x["code"] in {"JOURNEY_EVENT_DIGEST_INVALID","JOURNEY_VIEW_DIVERGES_FROM_EVENTS"} for x in report["issues"])


def test_canonical_question_registries_are_unique():
    root=Path(__file__).resolve().parents[2]
    for registry in (root/"packages").glob("*/question_registry.json"):
        data=json.loads(registry.read_text())
        ids=[q["question_id"] for q in data["questions"]]
        nodes=[q["node_id"] for q in data["questions"]]
        assert len(ids)==len(set(ids))
        assert len(nodes)==len(set(nodes))
        assert all(q.get("capture_for_journey") is True for q in data["questions"])
