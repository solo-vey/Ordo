#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(root: Path, playbook: dict) -> dict:
    state=_load(root/"manifests/VERSION_STATE.json")
    catalog=_load(root/"manifests/UPGRADE_IMPACT_CATALOG.json")
    used=set(playbook.get("constructs", []))
    lines=set(playbook.get("lines", ["language","framework"]))
    actions=[]
    rank={"no_action":0,"no_playbook_change":0,"recommended_revalidation":1,"migration_required_when_enabled":2,"migration_required":3,"upgrade_blocked":4}
    for release in catalog["releases"]:
        for change in release["changes"]:
            if not lines.intersection(change.get("lines", [])):
                continue
            constructs=set(change.get("constructs", []))
            applies=not constructs or bool(used.intersection(constructs))
            action=change["action"] if applies else "no_action"
            actions.append({"change_id":change["id"],"applies":applies,"action":action,"instruction":change["instruction"],"backlog":change.get("backlog",[])})
    decision=max((a["action"] for a in actions),key=lambda x:rank.get(x,0),default="no_action")
    return {
      "schema_version":"ordo.upgrade_impact_report.v1",
      "playbook_id":playbook.get("playbook_id","unknown"),
      "recorded_versions":playbook.get("versions",{}),
      "target_versions":{"language":state["language"]["version"],"framework":state["framework"]["version"]},
      "overall_decision":decision,
      "actions":actions,
      "automatic_rewrite":False
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("playbook",type=Path)
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=resolve(a.root,_load(a.playbook))
    text=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.output: a.output.write_text(text,encoding="utf-8")
    else: print(text,end="")

if __name__=="__main__": main()
