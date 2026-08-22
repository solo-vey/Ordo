#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,subprocess,sys,time,hashlib,os,zipfile,importlib.util,io,contextlib,runpy
import yaml
from pathlib import Path

PHASE_ORDER=["FAST","PRE_EDITOR","POST_EDITOR","RELEASE"]
PASS_STATUSES={"PASS","PASSED","SUCCESS","OK","READY","VALID"}
SIMULATION_CHECK_IDS={
    "simulation_evidence", "fixture_contract_closure", "runtime_gate_evidence",
    "defect_ownership", "simulation_kit_dependency_integrity",
    "alpha27_simulation_kit_012_upgrade", "alpha28_simulation_kit_013_upgrade",
    "simulation_kit_015_current",
}

def child_env():
    env=os.environ.copy()
    # Package-local validators are CLI subprocesses, not notebook kernels.
    # Prevent unrelated artifact_tool spreadsheet warmup from adding ~10s per validator process.
    env["OAI_IS_JUPYTER_KERNEL"]="0"
    return env

def watchdog_exec(cmd, *, timeout_seconds, long_running_reason, cwd, env, operation_id):
    wd=Path(__file__).resolve().parent/"run_with_watchdog.py"
    ledger=Path(cwd)/"reports"/"AUTHORING_EXECUTION_TIMING.jsonl"
    wcmd=[sys.executable,str(wd),"--timeout",str(int(timeout_seconds)),"--ledger",str(ledger),"--operation-id",str(operation_id)]
    if long_running_reason: wcmd += ["--long-running-reason",str(long_running_reason)]
    wcmd += ["--",*list(cmd)]
    outer=max(int(timeout_seconds)+10,20)
    p=subprocess.run(wcmd,cwd=cwd,capture_output=True,text=True,timeout=outer,env=env)
    return p

def jload(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def contained(root,p):
    try:
        Path(p).resolve().relative_to(Path(root).resolve()); return True
    except Exception: return False

def parse_json_tail(text):
    text=(text or "").strip()
    try: return json.loads(text)
    except Exception:
        # best effort: locate final JSON object
        starts=[i for i,c in enumerate(text) if c=="{"]
        for i in reversed(starts):
            try: return json.loads(text[i:])
            except Exception: pass
    return None


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def internal_laws(target,vibe):
    canonical=vibe/"PLAYBOOK_LAWS.md"
    guide=vibe/"canonical_support/guides/PLAYBOOK_LAWS.md"
    target_laws=target/"PLAYBOOK_LAWS.md"
    checks={
      "canonical_root_present":canonical.is_file(),
      "guide_present":guide.is_file(),
      "target_present":target_laws.is_file(),
    }
    missing_source_laws=[]
    if all(checks.values()):
        checks["root_matches_guide"]=sha256(canonical)==sha256(guide)
        checks["target_matches_canonical"]=sha256(target_laws)==sha256(canonical)
        source=vibe/"source/program.ordo.yaml"
        checks["source_present"]=source.is_file()
        if source.is_file():
            program=yaml.safe_load(source.read_text(encoding="utf-8")) or {}
            laws=((program.get("playbook_laws") or {}).get("laws") or [])
            text=canonical.read_text(encoding="utf-8")
            for law in laws:
                lid=str(law.get("id") or "")
                ltext=str(law.get("text") or "")
                if not lid or not ltext or lid not in text or ltext not in text:
                    missing_source_laws.append(lid or "<missing-id>")
            checks["source_laws_materialized_verbatim"]=not missing_source_laws
    ok=all(checks.values())
    return ok,{"status":"PASS" if ok else "FAIL","checks":checks,"target":str(target_laws),
               "missing_source_laws":missing_source_laws}

def internal_source_uniqueness(target):
    # The bundled canonical language is a reference corpus and may contain
    # examples. Only Vibe's executable source and an explicitly declared
    # derived projection participate in delivery-source uniqueness.
    programs=sorted(
        str(p.relative_to(target)).replace("\\","/")
        for p in target.rglob("program.ordo.yaml")
        if not p.is_relative_to(target / "canonical_support" / "language")
        and not p.is_relative_to(target / "cli_embedded")
    )
    canonical="source/program.ordo.yaml"
    derived="runtime_projection/program.ordo.yaml"
    provenance=target/"runtime_projection/ACTOR_PROJECTION_PROVENANCE.json"
    unexpected=[p for p in programs if p not in {canonical,derived}]
    checks={
      "canonical_program_present_exactly_once":programs.count(canonical)==1,
      "no_unexpected_program_sources":not unexpected,
      "derived_runtime_projection_declared":derived not in programs or provenance.is_file(),
    }
    ok=all(checks.values())
    return ok,{"status":"PASS" if ok else "FAIL","program_files":programs,"unexpected":unexpected,"checks":checks}

def internal_editor_graph(target):
    src=target/"source/program.ordo.yaml"
    d=yaml.safe_load(src.read_text(encoding="utf-8"))
    nodes={x["id"]:x for x in (d.get("nodes") or []) if isinstance(x,dict) and x.get("id")}
    gates={x["id"]:x for x in (d.get("gates") or []) if isinstance(x,dict) and x.get("id")}
    ext=set((d.get("graph_contract") or {}).get("external_terminal_targets") or [])
    ids=set(nodes)|set(gates)
    def targets(obj,is_gate=False):
        out=[]
        def rec(v):
            if isinstance(v,dict):
                for k,x in v.items():
                    if k=="next" and isinstance(x,str): out.append(x)
                    else: rec(x)
            elif isinstance(v,list):
                for x in v: rec(x)
        if is_gate:
            for k in ("on_pass","on_fail"):
                x=obj.get(k)
                if isinstance(x,str) and x.casefold() not in {"block","continue","retry","stop","warn"}:
                    out.append(x)
        else: rec(obj)
        return out
    adj={k:targets(v,False) for k,v in nodes.items()}
    adj.update({k:targets(v,True) for k,v in gates.items()})
    entry=(d.get("graph_contract") or {}).get("entry_node")
    seen=set(); stack=[entry]
    while stack:
        cur=stack.pop()
        if cur in seen or cur not in ids: continue
        seen.add(cur)
        for x in adj.get(cur,[]):
            if x in ids: stack.append(x)
    no_route=sorted(k for k in ids if not adj.get(k) and k not in ext)
    unreachable=sorted(ids-seen)
    checks={"all_nodes_and_gates_reachable":not unreachable,
            "all_nonterminal_elements_have_route":not no_route,
            "all_declared_gates_reached":all(g in seen for g in gates)}
    ok=all(checks.values())
    return ok,{"status":"PASS" if ok else "FAIL","entry":entry,"reachable":len(seen),"total":len(ids),
               "unreachable":unreachable,"no_route":no_route,"checks":checks}

ZERO_KEYS={"checked_artifacts","checked_contracts","expected_outputs","evaluated_assertions",
           "behaviorally_evaluated_assertions","checked_items","checks_executed"}
EMPTY_EVIDENCE_KEYS={"evidence","check_results","checks","findings"}

def internal_evidence_quality(report):
    p=Path(report)
    if not p.is_file():
        return False,{"status":"FAIL","code":"EVIDENCE_REPORT_MISSING","path":str(p)}
    try: d=json.loads(p.read_text(encoding="utf-8"))
    except Exception as e: return False,{"status":"FAIL","code":"EVIDENCE_REPORT_INVALID_JSON","error":str(e)}
    findings=[]
    def walk(v,path="$"):
        if isinstance(v,dict):
            yield path,v
            for k,x in v.items(): yield from walk(x,f"{path}.{k}")
        elif isinstance(v,list):
            for i,x in enumerate(v): yield from walk(x,f"{path}[{i}]")
    for path,obj in walk(d):
        status=str(obj.get("status","")).upper()
        if status not in PASS_STATUSES: continue
        for k in ZERO_KEYS:
            if k in obj and obj[k]==0:
                findings.append({"path":path,"code":"VACUOUS_PASS_ZERO_COUNT","field":k})
        for k in EMPTY_EVIDENCE_KEYS:
            if k in obj and obj[k] in ([],{},None,""):
                semantic=any(tok in path.lower() for tok in ("gate","semantic","consistency","artifact","verification","readiness"))
                if semantic: findings.append({"path":path,"code":"PASS_WITH_EMPTY_EVIDENCE","field":k})
    ok=not findings
    return ok,{"status":"PASS" if ok else "FAIL","report":str(p),"findings":findings}


def internal_ordo_cli(argv,vibe,target):
    pkg=str(vibe/"cli_embedded"/"ordo_pkg")
    if pkg not in sys.path: sys.path.insert(0,pkg)
    from ordo.cli import main as ordo_main
    out=io.StringIO(); err=io.StringIO()
    old=os.getcwd()
    try:
        os.chdir(target)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc=ordo_main(list(argv))
            except SystemExit as e:
                rc=e.code if isinstance(e.code,int) else 1
    except Exception as e:
        rc=2
        err.write(f"{type(e).__name__}: {e}")
    finally:
        os.chdir(old)
    return int(rc or 0),out.getvalue(),err.getvalue()

def command_for(check,target,vibe):
    runner=check["runner"]; args=check.get("args") or {}
    py=sys.executable; oa=str(vibe/"tools/ordo_authoring.py")
    source=target/"source/program.ordo.yaml"
    if runner=="ordo_lint": return [py,oa,"lint",str(source)]
    if runner=="ordo_compile": return [py,oa,"compile",str(target)]
    if runner=="ordo_test": return [py,oa,"test",str(target)]
    if runner=="ordo_coverage": return [py,oa,"coverage",str(target)]
    if runner=="ordo_runtime_status": return [py,oa,"runtime-status",str(target)]
    if runner=="ordo_verify_targets": return [py,oa,"verify-targets",str(target)]
    if runner=="ordo_clean_check": return [py,oa,"clean-check",str(target),"--profile",str(args.get("profile","strict"))]
    if runner=="python_script":
        script=target/str(args.get("script",""))
        if not contained(target,script): raise ValueError("PYTHON_SCRIPT_OUTSIDE_PACKAGE")
        cmd=[py,str(script)]
        for x in args.get("argv",[]) or []:
            cmd.append(str(x).replace("{package_root}",str(target)))
        return cmd
    return None

def external_evidence(check,target):
    args=check.get("args") or {}
    p=target/str(args.get("path",""))
    if not contained(target,p):
        return False,{"code":"EXTERNAL_EVIDENCE_OUTSIDE_PACKAGE","path":str(p)}
    if not p.is_file():
        return False,{"code":"EXTERNAL_EVIDENCE_MISSING","path":str(p)}
    try: d=jload(p)
    except Exception as e: return False,{"code":"EXTERNAL_EVIDENCE_INVALID_JSON","error":str(e),"path":str(p)}
    accepted={str(x).upper() for x in args.get("accepted_statuses",list(PASS_STATUSES))}
    status=str(d.get("status",d.get("result",d.get("overall_status","")))).upper()
    ok=status in accepted
    return ok,{"path":str(p),"status":status,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("--verification-profile",default="verification_profile.json")
    ap.add_argument("--vibe-root",default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--through",choices=PHASE_ORDER,default="PRE_EDITOR")
    ap.add_argument("--report",default="reports/VERIFICATION_EVIDENCE_SUMMARY.json")
    ap.add_argument("--only",default="",help="Comma-separated check ids for incremental execution after validating the full profile.")
    ap.add_argument("--checkpoint-satisfied",default="",help="Comma-separated dependency check ids already PASS at a trusted checkpoint.")
    ap.add_argument("--include-simulation",action="store_true",help="Run checks that require the separately supplied Simulation Kit.")
    ap.add_argument("--profile",choices=("BASE","EDITOR","SIMULATION"),default="BASE",help="Select optional dependency contour.")
    a=ap.parse_args()
    target=Path(a.package).resolve(); vibe=Path(a.vibe_root).resolve()
    if a.profile == "SIMULATION":
        a.include_simulation = True
    prof=(target/a.verification_profile).resolve()
    if not prof.is_file():
        print(json.dumps({"status":"FAIL","code":"VERIFICATION_PROFILE_MISSING","path":str(prof)},indent=2)); return 2
    vp=subprocess.run([sys.executable,str(vibe/"tools/validate_verification_profile.py"),str(prof),"--vibe-root",str(vibe)],
                      capture_output=True,text=True,env=child_env())
    if vp.returncode:
        print(vp.stdout or vp.stderr); return 2
    d=jload(prof); cutoff=PHASE_ORDER.index(a.through)
    selected=[c for c in d["checks"] if PHASE_ORDER.index(c["phase"])<=cutoff]
    only_ids={x for x in a.only.split(',') if x}
    checkpoint_satisfied={x for x in a.checkpoint_satisfied.split(',') if x}
    if only_ids:
        known={c['id'] for c in selected}
        unknown=sorted(only_ids-known)
        if unknown:
            print(json.dumps({'status':'FAIL','code':'ONLY_CHECK_UNKNOWN','unknown':unknown},indent=2)); return 2
        selected=[c for c in selected if c['id'] in only_ids]
    selected_ids={c["id"] for c in selected}
    results={}; rows=[]; overall=True; start=time.time()
    for c in selected:
        cid=c["id"]; required=c["required"]; deps=c.get("depends_on",[]) or []
        print(f"START {c['phase']} {cid} [{c['runner']}]", flush=True)
        if cid in SIMULATION_CHECK_IDS and not a.include_simulation:
            row={"id":cid,"runner":c["runner"],"phase":c["phase"],"required":False,"status":"SKIP","code":"OPTIONAL_SIMULATION_KIT_NOT_ENABLED","invariants":c.get("invariants",[])}
            results[cid]=row; rows.append(row)
            print(f"SKIP {c['phase']} {cid} [optional simulation dependency]", flush=True)
            continue
        missing_deps=[x for x in deps if x not in selected_ids and x not in checkpoint_satisfied]
        failed_deps=[x for x in deps if x in results and results[x]["status"]!="PASS"]
        if missing_deps or failed_deps:
            row={"id":cid,"runner":c["runner"],"phase":c["phase"],"required":required,"status":"FAIL" if required else "SKIP",
                 "code":"DEPENDENCY_NOT_SATISFIED","missing_dependencies":missing_deps,"failed_dependencies":failed_deps,
                 "invariants":c.get("invariants",[])}
            results[cid]=row; rows.append(row)
            print(f"{row['status']} {c['phase']} {cid} [dependency] ", flush=True)
            overall=overall and not required; continue
        ts=time.time()
        if c["runner"] in {"ordo_lint","ordo_compile","ordo_test","ordo_coverage","ordo_runtime_status","ordo_verify_targets","ordo_clean_check",
                         "ordo_validate_artifacts","ordo_consistency","ordo_validate_output","ordo_validate_lock",
                         "ordo_check_conflicts","ordo_repo_check"}:
            args=c.get("args") or {}
            source=target/"source/program.ordo.yaml"
            argv={
              "ordo_lint":["lint",str(source)],
              "ordo_compile":["compile",str(target)],
              "ordo_test":["test",str(target)],
              "ordo_coverage":["coverage",str(target)],
              "ordo_runtime_status":["runtime-status",str(target)],
              "ordo_verify_targets":["verify-targets",str(target)],
              "ordo_clean_check":["clean-check",str(target),"--profile",str(args.get("profile","strict"))],
              "ordo_validate_artifacts":["validate-artifacts",str(target)],
              "ordo_consistency":["consistency",str(target)],
              "ordo_validate_output":["validate-output",str(target)],
              "ordo_validate_lock":["validate-lock",str(target)],
              "ordo_check_conflicts":["check-conflicts",str(target)],
              "ordo_repo_check":["repo-check",str(target)]
            }[c["runner"]]
            rc,stdout,stderr=internal_ordo_cli(argv,vibe,target)
            detail={"stderr_tail":stderr[-2000:],"argv":argv}
        elif c["runner"]=="external_evidence":
            ok,detail=external_evidence(c,target); rc=0 if ok else 1; stdout=json.dumps(detail,ensure_ascii=False)
        elif c["runner"]=="laws_verbatim":
            ok,detail=internal_laws(target,vibe); rc=0 if ok else 1; stdout=json.dumps(detail,ensure_ascii=False)
        elif c["runner"]=="delivery_source_uniqueness":
            ok,detail=internal_source_uniqueness(target); rc=0 if ok else 1; stdout=json.dumps(detail,ensure_ascii=False)
        elif c["runner"]=="editor_runtime_graph":
            ok,detail=internal_editor_graph(target); rc=0 if ok else 1; stdout=json.dumps(detail,ensure_ascii=False)
        elif c["runner"]=="evidence_quality":
            rp=target/str((c.get("args") or {}).get("report",""))
            ok,detail=internal_evidence_quality(rp); rc=0 if ok else 1; stdout=json.dumps(detail,ensure_ascii=False)
        elif c["runner"]=="generated_playbook_contract":
            checker=vibe/"tools/verify_generated_playbook_contract.py"
            spec=importlib.util.spec_from_file_location("vibe_generated_playbook_contract",checker)
            mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            detail=mod.validate_package(target,vibe_root=vibe,target=str((c.get("args") or {}).get("target","language_core")))
            ok=detail.get("status")=="PASS"; rc=0 if ok else 1; stdout=json.dumps(detail,ensure_ascii=False)
        elif c["runner"]=="execution_responsibility_map":
            checker=target/"tools/verify_execution_responsibility_map.py"
            if not checker.is_file(): checker=vibe/"tools/verify_execution_responsibility_map.py"
            spec=importlib.util.spec_from_file_location("vibe_exec_map_validator",checker)
            mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            detail=mod.validate_package(target)
            ok=detail.get("status")=="PASS"; rc=0 if ok else 1; stdout=json.dumps(detail,ensure_ascii=False)
        elif c["runner"]=="artifact_materialization_registry":
            checker=target/"tools/validate_artifact_materialization_registry.py"
            if not checker.is_file(): checker=vibe/"tools/validate_artifact_materialization_registry.py"
            spec=importlib.util.spec_from_file_location("vibe_artifact_registry_validator",checker)
            mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            detail=mod.validate_package(target)
            ok=detail.get("status")=="PASS"; rc=0 if ok else 1; stdout=json.dumps(detail,ensure_ascii=False)
        elif c["runner"]=="verification_truth":
            checker=vibe/"tools/check_verification_truth.py"
            p=subprocess.run([sys.executable,str(checker),str(target)],capture_output=True,text=True,timeout=30,env=child_env())
            rc=p.returncode; stdout=p.stdout; detail={"stderr_tail":p.stderr[-2000:],"script":str(checker)}
        elif c["runner"]=="trusted_python_regression":
            script=(target/str((c.get("args") or {}).get("script",""))).resolve()
            allowed_root=(vibe/"tools").resolve()
            if not contained(allowed_root,script) or not script.name.startswith("test_"):
                rc=2; stdout=json.dumps({"status":"FAIL","code":"TRUSTED_REGRESSION_PATH_REJECTED","script":str(script)})
                detail={}
            else:
                trusted_stdout_path=target/"reports"/f".trusted_{cid}.stdout.log"
                trusted_stderr_path=target/"reports"/f".trusted_{cid}.stderr.log"
                trusted_stdout_path.parent.mkdir(parents=True,exist_ok=True)
                try:
                    with trusted_stdout_path.open("w",encoding="utf-8") as so, trusted_stderr_path.open("w",encoding="utf-8") as se:
                        pass
                    p=watchdog_exec([sys.executable,str(script)],timeout_seconds=int(c.get("timeout_seconds",60)),long_running_reason=c.get("long_running_reason"),cwd=target,env=child_env(),operation_id=cid)
                    rc=p.returncode
                    stdout=p.stdout
                    stderr_text=p.stderr
                    trusted_stdout_path.write_text(stdout or "",encoding="utf-8")
                    trusted_stderr_path.write_text(stderr_text or "",encoding="utf-8")
                    detail={"stderr_tail":stderr_text[-2000:],"script":str(script),"execution":"watchdog_subprocess_isolated"}
                except subprocess.TimeoutExpired:
                    rc=124
                    stdout=trusted_stdout_path.read_text(encoding="utf-8",errors="ignore") if trusted_stdout_path.is_file() else ""
                    stderr_text=trusted_stderr_path.read_text(encoding="utf-8",errors="ignore") if trusted_stderr_path.is_file() else ""
                    detail={"code":"TIMEOUT","timeout_seconds":int(c.get("timeout_seconds",120)),"stderr_tail":stderr_text[-2000:],"script":str(script),"execution":"subprocess_isolated_file_backed"}
        else:
            try: cmd=command_for(c,target,vibe)
            except Exception as e:
                cmd=None; rc=2; stdout=""; detail={"error":str(e)}
            if cmd is None:
                rc=2; stdout=json.dumps({"error":"RUNNER_NOT_EXECUTABLE","runner":c["runner"]}); detail={}
            else:
                try:
                    p=watchdog_exec(cmd,timeout_seconds=int(c.get("timeout_seconds",60)),long_running_reason=c.get("long_running_reason"),cwd=target,env=child_env(),operation_id=cid)
                    rc=p.returncode; stdout=p.stdout; detail={"stderr_tail":p.stderr[-2000:],"command":cmd,"execution":"watchdog_subprocess"}
                except subprocess.TimeoutExpired as e:
                    rc=124; stdout=e.stdout or ""; detail={"code":"TIMEOUT","timeout_seconds":int(c.get("timeout_seconds",120)),"command":cmd}
        parsed=parse_json_tail(stdout)
        status="PASS" if rc==0 else ("FAIL" if required else "WARN")
        row={"id":cid,"runner":c["runner"],"phase":c["phase"],"required":required,"status":status,"returncode":rc,
             "elapsed_s":round(time.time()-ts,3),"invariants":c.get("invariants",[]),
             "evidence":parsed if parsed is not None else {"stdout_tail":(stdout or "")[-3000:],**detail}}
        results[cid]=row; rows.append(row)
        print(f"{status} {c['phase']} {cid} ({row['elapsed_s']}s)", flush=True)
        if required and status!="PASS": overall=False
    required_invariants=sorted({i for c in selected if c.get("required") for i in c.get("invariants",[])})
    passed_invariants=sorted({i for r in rows if r["status"]=="PASS" for i in r.get("invariants",[])})
    uncovered=[x for x in required_invariants if x not in passed_invariants]
    if uncovered: overall=False
    report={
      "schema_version":"1.0","profile_id":d["profile_id"],"playbook_revision":d["playbook_revision"],
      "package":str(target),"through":a.through,"status":"PASS" if overall else "FAIL",
      "elapsed_s":round(time.time()-start,3),"checks":rows,
      "required_invariants":required_invariants,"passed_invariants":passed_invariants,"unverified_required_invariants":uncovered
    }
    rp=(target/a.report).resolve()
    if not contained(target,rp): raise SystemExit("REPORT_OUTSIDE_PACKAGE")
    rp.parent.mkdir(parents=True,exist_ok=True); rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"report":str(rp),"through":a.through,
                      "checks_total":len(rows),"checks_passed":sum(r["status"]=="PASS" for r in rows),
                      "unverified_required_invariants":uncovered,"elapsed_s":report["elapsed_s"]},ensure_ascii=False,indent=2))
    return 0 if overall else 1
if __name__=="__main__":
    import os
    rc=main()
    try:
        sys.stdout.flush(); sys.stderr.flush()
    finally:
        os._exit(int(rc))
