from pathlib import Path
import copy
import yaml

from ordo.prompt_governance import audit_prompt_governance, _audit_candidates

ROOT = Path(__file__).resolve().parents[2]


def test_repository_prompt_governance_passes():
    r = audit_prompt_governance(ROOT)
    assert r["status"] == "passed", r
    assert r["blocking_issues"] == []
    assert len(r["package_results"]) == 4
    assert r["apf_registry"]["registry_entries"] == 6
    assert r["candidate_governance"]["candidate_count"] == 2
    assert r["internal_mini_prompt_review"]["status"] == "passed"


def test_only_registry_package_has_active_registry():
    r = audit_prompt_governance(ROOT)
    active = [x["package"] for x in r["package_results"] if x["registry_mode"] == "active"]
    assert active == ["history_event_guided_intake"]


def test_pending_candidates_remain_inactive():
    r = audit_prompt_governance(ROOT)
    for c in r["candidate_governance"]["candidates"]:
        assert c["candidate_status"] == "proposed"
        assert c["review_status"] == "pending"
        assert c["activation_allowed"] is False


def test_candidate_audit_blocks_preapproval_activation(tmp_path):
    src = ROOT / "integrations" / "apf" / "v0.1.0-rc.18" / "improvements" / "playbook_authored_mini_prompts"
    dst = tmp_path / "improvements" / "playbook_authored_mini_prompts"
    import shutil
    shutil.copytree(src, dst)
    review = next(dst.glob("pilots/*/reviews/*.yaml"))
    doc = yaml.safe_load(review.read_text())
    doc["review_record"]["activation_allowed"] = True
    review.write_text(yaml.safe_dump(doc, sort_keys=False))
    result = _audit_candidates(tmp_path)
    assert result["status"] == "failed"
    assert any(x["issue"] == "preapproval_activation" for x in result["errors"])
