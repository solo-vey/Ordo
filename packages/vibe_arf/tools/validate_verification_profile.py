#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path

PHASES={"FAST","PRE_EDITOR","POST_EDITOR","RELEASE"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("profile")
    ap.add_argument("--vibe-root", default=str(Path(__file__).resolve().parents[1]))
    a=ap.parse_args()
    p=Path(a.profile).resolve()
    root=Path(a.vibe_root).resolve()
    registry=json.loads((root/"source/verification-runner-registry.json").read_text(encoding="utf-8"))
    runners=set(registry["runners"])
    errors=[]
    try: d=json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(json.dumps({"status":"FAIL","errors":[f"PROFILE_JSON_INVALID: {e}"]},indent=2)); return 1
    for k in ("schema_version","profile_id","playbook_revision","checks"):
        if k not in d: errors.append(f"MISSING_TOP_LEVEL:{k}")
    checks=d.get("checks",[])
    if not isinstance(checks,list) or not checks: errors.append("CHECKS_REQUIRED")
    ids=[]
    for i,c in enumerate(checks if isinstance(checks,list) else []):
        path=f"checks[{i}]"
        if not isinstance(c,dict):
            errors.append(f"{path}:NOT_OBJECT"); continue
        for k in ("id","runner","phase","required"):
            if k not in c: errors.append(f"{path}:MISSING:{k}")
        cid=c.get("id")
        if cid in ids: errors.append(f"{path}:DUPLICATE_ID:{cid}")
        ids.append(cid)
        if c.get("runner") not in runners: errors.append(f"{path}:UNKNOWN_RUNNER:{c.get('runner')}")
        if c.get("phase") not in PHASES: errors.append(f"{path}:INVALID_PHASE:{c.get('phase')}")
        if not isinstance(c.get("required"),bool): errors.append(f"{path}:REQUIRED_NOT_BOOL")
        if c.get("runner")=="python_script":
            script=str((c.get("args") or {}).get("script",""))
            if not script: errors.append(f"{path}:PYTHON_SCRIPT_PATH_REQUIRED")
            elif Path(script).is_absolute() or ".." in Path(script).parts:
                errors.append(f"{path}:PYTHON_SCRIPT_MUST_BE_PACKAGE_LOCAL")
        timeout=int(c.get('timeout_seconds',60))
        if timeout>60 and not str(c.get('long_running_reason') or '').strip(): errors.append(f"{path}:LONG_RUNNING_REASON_REQUIRED")
        if c.get("runner")=="external_evidence":
            if not str((c.get("args") or {}).get("path","")):
                errors.append(f"{path}:EXTERNAL_EVIDENCE_PATH_REQUIRED")
    idset=set(ids)
    runner_by_phase={p:set() for p in PHASES}
    for c in checks if isinstance(checks,list) else []:
        if isinstance(c,dict) and c.get("phase") in PHASES and c.get("required") is True:
            runner_by_phase[c["phase"]].add(c.get("runner"))
    for i,c in enumerate(checks if isinstance(checks,list) else []):
        if isinstance(c,dict):
            for dep in c.get("depends_on",[]) or []:
                if dep not in idset: errors.append(f"checks[{i}]:UNKNOWN_DEPENDENCY:{dep}")
    contract=registry.get("mandatory_profile_contract",{})
    for phase,required_runners in contract.items():
        missing=sorted(set(required_runners)-runner_by_phase.get(phase,set()))
        for runner in missing:
            errors.append(f"MANDATORY_RUNNER_MISSING:{phase}:{runner}")
    status="PASS" if not errors else "FAIL"
    print(json.dumps({"status":status,"profile":str(p),"check_count":len(checks) if isinstance(checks,list) else 0,"errors":errors},ensure_ascii=False,indent=2))
    return 0 if status=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())
