from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"reports/m78_1_apf_internal_mini_prompt_review/M78_1_APF_INTERNAL_MINI_PROMPT_APPLICABILITY_REVIEW.json"

def load(): return json.loads(REPORT.read_text())

def test_review_complete():
    r=load(); assert r["summary"]["reviewed_objects"] >= 5

def test_no_internal_candidates_or_activation():
    r=load(); assert r["summary"]["new_prompt_candidates"] == 0; assert r["summary"]["internal_prompts_to_activate"] == 0

def test_authoritative_steps_prohibit_prompts():
    r=load(); prohibited={x["object_id"] for x in r["reviews"] if x["classification"]=="prompt_prohibited"}; assert {"GATE_ORDER_CONFIRMATION_GATE","CSG_RUNTIME_CLASSIFICATION"} <= prohibited

def test_reopen_policy_is_evidence_based():
    r=load(); assert len(r["reopen_conditions"]) >= 4; assert "two independent replay runs" in r["reopen_conditions"][0]
