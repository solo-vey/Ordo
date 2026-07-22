import json
from pathlib import Path
from cli.ordo.apf_replay import evaluate_replay

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "cli/tests/fixtures/apf_real_case_replay/history_event_replay_cases.json"


def test_all_real_case_replays_pass():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    results = [evaluate_replay(case) for case in data["cases"]]
    assert all(r.status == "passed" for r in results), [r.errors for r in results]


def test_protected_state_change_fails():
    case = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"][0]
    case["post_state"]["event_alias"] = "BROKEN"
    result = evaluate_replay(case)
    assert result.status == "failed"
    assert "PROTECTED_STATE_CHANGED" in result.errors


def test_low_analyst_experience_fails():
    case = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"][0]
    case["analyst_experience"]["active_question_clarity"] = 0
    result = evaluate_replay(case)
    assert result.status == "failed"
    assert "ANALYST_EXPERIENCE_BELOW_THRESHOLD" in result.errors


def test_handoff_required_is_enforced():
    case = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"][3]
    case["post_state"]["handoff_ready"] = False
    result = evaluate_replay(case)
    assert "HANDOFF_NOT_READY" in result.errors
