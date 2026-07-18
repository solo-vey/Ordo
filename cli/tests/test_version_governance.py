import json
from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[2]

def load(rel): return json.loads((ROOT/rel).read_text())

def test_version_state_and_ledger_agree():
    s=load("manifests/VERSION_STATE.json"); l=load("manifests/RELEASE_LEDGER.json")
    assert l["current_release"]==s["release_id"]
    r=l["releases"][-1]
    assert r["language_version"]==s["language"]["version"]
    assert r["framework_version"]==s["framework"]["version"]

def test_closed_backlog_items_have_completed_in():
    b=load("manifests/CONSOLIDATED_BACKLOG.json")
    missing=[x["id"] for x in b["items"] if x.get("status") in {"closed","merged_superseded"} and not x.get("completed_in") and x["id"] in set(load("manifests/RELEASE_LEDGER.json")["releases"][-1]["completed_backlog_items"])]
    assert missing==[]

def test_packages_declare_compatibility():
    for p in (ROOT/"packages").glob("*/ordo.yml"):
        t=p.read_text()
        assert "language_version_constraint:" in t
        assert "framework_version_constraint:" in t
        assert "version_state:" in t

def test_upgrade_resolver_is_fail_review_not_auto_rewrite(tmp_path):
    spec=importlib.util.spec_from_file_location("upgrade",ROOT/"tools/resolve_upgrade_impact.py")
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    report=mod.resolve(ROOT,{"playbook_id":"p","versions":{"language":"0.12"},"constructs":["startup_package_profile"]})
    assert report["overall_decision"]=="migration_required"
    assert report["automatic_rewrite"] is False

def test_upgrade_resolver_ignores_unrelated_constructs():
    spec=importlib.util.spec_from_file_location("upgrade2",ROOT/"tools/resolve_upgrade_impact.py")
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    report=mod.resolve(ROOT,{"playbook_id":"p","constructs":["UNRELATED"]})
    assert all(not a["applies"] for a in report["actions"] if a["change_id"]!="CHG-010")
