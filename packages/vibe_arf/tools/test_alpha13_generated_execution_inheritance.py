#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,tempfile,shutil,importlib.util,hashlib,yaml
R=Path(__file__).resolve().parents[1]
checks={}

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

validator=load_module("a13_resp",R/"tools/verify_execution_responsibility_map.py")
materializer=load_module("a13_mat",R/"tools/materialize_generated_playbook_verification.py")

# Self-hosted classification.
self_result=validator.validate_package(R)
checks["self_responsibility_map_passes"]=self_result.get("status")=="PASS"

# Laws: exact copy/hash chain and source-contract text presence.
law_paths=[R/"PLAYBOOK_LAWS.md",R/"canonical_support/guides/PLAYBOOK_LAWS.md",
           R/"canonical_support/output_templates/PLAYBOOK_LAWS.md"]
checks["laws_copies_present"]=all(p.is_file() for p in law_paths)
if checks["laws_copies_present"]:
    checks["laws_copies_match"]=len({hashlib.sha256(p.read_bytes()).hexdigest() for p in law_paths})==1
    source=yaml.safe_load((R/"source/program.ordo.yaml").read_text(encoding="utf-8")) or {}
    text=law_paths[0].read_text(encoding="utf-8")
    laws=((source.get("playbook_laws") or {}).get("laws") or [])
    checks["source_laws_materialized"]=all(str(x.get("id") or "") in text and str(x.get("text") or "") in text for x in laws)
else:
    checks["laws_copies_match"]=False; checks["source_laws_materialized"]=False

# Mandatory profile contract and exact generated profile.
registry=json.loads((R/"source/verification-runner-registry.json").read_text(encoding="utf-8"))
mandatory=set((registry.get("mandatory_profile_contract") or {}).get("PRE_EDITOR") or [])
checks["registry_requires_responsibility_runner"]="execution_responsibility_map" in mandatory
profile=json.loads((R/"verification_profile.json").read_text(encoding="utf-8"))
checks["profile_contains_responsibility_runner"]=any(
    c.get("runner")=="execution_responsibility_map" and c.get("required") is True
    for c in profile.get("checks",[])
)

# Materialization contract must install inherited assets but leave execution classification fail-closed.
with tempfile.TemporaryDirectory() as td:
    target=Path(td)/"sample"; target.mkdir()
    shutil.copytree(R/"source",target/"source")
    result=materializer.materialize(target,R,generate_profile=False)
    checks["materializer_runs"]=result.get("status")=="PASS"
    required=("PLAYBOOK_LAWS.md","verification/EXECUTION_RESPONSIBILITY_MAP.json",
              "verification/INVARIANT_REGISTER.json","verification/PROFILE_EXTENSIONS.json",
              "tools/verify_execution_responsibility_map.py")
    checks["materializer_outputs_complete"]=all((target/r).is_file() for r in required)
    scaffold=validator.validate_package(target)
    checks["unclassified_scaffold_fails_closed"]=scaffold.get("status")=="FAIL" and bool(scaffold.get("findings"))

status="PASS" if all(checks.values()) else "FAIL"
print(json.dumps({"status":status,"checks":checks},ensure_ascii=False,indent=2))
raise SystemExit(0 if status=="PASS" else 1)
