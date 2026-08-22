#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import zipfile
from collections import deque
from pathlib import Path
from typing import Any, Iterable

import yaml

CANONICAL_RESERVED_ROUTE_TARGETS={"STOP"}
EDITOR_COMPILED_PATTERNS=(
    "runtime_semantic_plan.json",
    "editor_runtime_plan.json",
    "runtime-semantic-plan.json",
)


def _walk(v: Any, path: str="$") -> Iterable[tuple[str,Any]]:
    yield path,v
    if isinstance(v,dict):
        for k,x in v.items():
            yield from _walk(x,f"{path}.{k}")
    elif isinstance(v,list):
        for i,x in enumerate(v):
            yield from _walk(x,f"{path}[{i}]")


def _strings(v: Any) -> Iterable[str]:
    if isinstance(v,str):
        yield v
    elif isinstance(v,dict):
        for x in v.values(): yield from _strings(x)
    elif isinstance(v,list):
        for x in v: yield from _strings(x)


def _route_targets(value: Any) -> list[str]:
    """Extract graph targets while ignoring state/data payload strings."""
    out=[]
    def rec(v: Any, parent_key: str|None=None):
        if isinstance(v,str):
            if parent_key in {"next","to","on_pass","on_fail","pass_to","fail_to"}:
                if v and not v.startswith("$"):
                    out.append(v)
            return
        if isinstance(v,dict):
            for k,x in v.items():
                if k in {"update_state","state","set_state","patch","artifact","package","metadata","bindings","inputs","outputs"}:
                    continue
                if k in {"next","to","on_pass","on_fail","pass_to","fail_to"}:
                    rec(x,k)
                elif isinstance(x,(dict,list)):
                    # on_answer outcome branches and transition objects may contain nested route keys.
                    rec(x,k)
            return
        if isinstance(v,list):
            for x in v: rec(x,parent_key)
    if isinstance(value,str):
        if value and not value.startswith("$"):
            out.append(value)
    else:
        rec(value,None)
    return list(dict.fromkeys(out))


def _element_targets(record: dict[str,Any], *, is_gate: bool=False) -> list[str]:
    out=[]
    if is_gate:
        for k in ("on_pass","on_fail","pass_to","fail_to"):
            out.extend(_route_targets(record.get(k)))
        return list(dict.fromkeys(out))
    if isinstance(record.get("next"),str): out.extend(_route_targets(record.get("next")))
    for k in ("on_answer","transitions"):
        out.extend(_route_targets(record.get(k)))
    nav=record.get("navigation_contract")
    if isinstance(nav,dict): out.extend(_route_targets(nav.get("allowed_to")))
    return list(dict.fromkeys(out))


def _external_terminals(program: dict[str,Any]) -> set[str]:
    ext=set()
    gc=program.get("graph_contract")
    if isinstance(gc,dict):
        ext.update(str(x) for x in (gc.get("external_terminal_targets") or []) if isinstance(x,str) and x)
    for item in program.get("terminals") or []:
        if isinstance(item,str) and item: ext.add(item)
        elif isinstance(item,dict) and isinstance(item.get("id"),str): ext.add(item["id"])
    return ext


def _editor_package_tool_declared(node: dict[str,Any]) -> bool:
    node_context=node.get("node_context") if isinstance(node.get("node_context"),dict) else {}
    allowed=node_context.get("allowed_tools") if isinstance(node_context.get("allowed_tools"),list) else []
    paths=[str(x).strip() for x in allowed if isinstance(x,str) and str(x).strip()]
    answer_type=str(node.get("answer_type") or "").casefold()
    structured=answer_type in {"structured_record","structured","json","object"}
    executable=any(x.casefold().endswith((".py",".js",".sh")) for x in paths)
    has_on_answer=isinstance(node.get("on_answer"),dict) and bool(node.get("on_answer"))
    text=json.dumps(node,ensure_ascii=False,default=str)
    declared=bool(re.search(r"(?:deterministic\s+helper|package\s+tool|allowed_tools|do\s+not\s+simulate\s+the\s+result)",text,re.I))
    return bool(paths and structured and executable and has_on_answer and declared)


def _owner(node: dict[str,Any]) -> str:
    ec=node.get("execution_contract") or {}
    if str(ec.get("runtime_executor") or "").casefold()=="package_tool" or _editor_package_tool_declared(node):
        return "deterministic"
    owner=str(ec.get("owner") or "").casefold()
    if owner in {"human","analyst","user"}: return "human"
    if owner in {"model","ai","semantic_model"}: return "model"
    if owner in {"deterministic","machine","tool"}: return "deterministic"
    ic=str(((node.get("node_context") or {}).get("interaction_class") or "")).upper()
    if ic=="USER_FACING": return "human"
    if ic=="MODEL_INTERNAL": return "model"
    if ic=="MACHINE_INTERNAL": return "deterministic"
    typ=str(node.get("type") or "").casefold()
    action=str(node.get("action") or "").upper()
    if typ in {"human_decision","human","question"}: return "human"
    if typ=="automatic" and action.startswith("AI."): return "model"
    if action.startswith(("PACKAGE.","DOCUMENT.","CLI.","PYTHON.")): return "deterministic"
    return "unknown"


def _branch_updates(node: dict[str,Any]) -> list[dict[str,Any]]:
    oa=node.get("on_answer")
    out=[]
    if not isinstance(oa,dict): return out
    if isinstance(oa.get("update_state"),dict): out.append(oa["update_state"])
    for k,v in oa.items():
        if k in {"next","update_state"}: continue
        if isinstance(v,dict) and isinstance(v.get("update_state"),dict): out.append(v["update_state"])
    return out


def _all_update_state(node: dict[str,Any]) -> dict[str,Any]:
    merged={}
    for d in _branch_updates(node): merged.update(d)
    if isinstance(node.get("update_state"),dict): merged.update(node["update_state"])
    return merged


def _is_validation_run(node: dict[str,Any]) -> bool:
    nid=str(node.get("id") or "").upper()
    text=" ".join(str(node.get(k) or "") for k in ("description","purpose","title","action")).lower()
    ec=node.get("execution_contract") or {}
    runtime_tool=str(ec.get("runtime_executor") or "").casefold()=="package_tool"
    owner_det=_owner(node)=="deterministic"
    validation_marker=bool(re.search(r"\b(validate|validator|validation|verify|verification|check|lint|test)\b",text))
    # Context builders/package assemblers may mention validation evidence but are not validation RUN executors.
    return owner_det and (nid.startswith("N_RUN_") or (runtime_tool and validation_marker))


def _replay_zip_status(path: Path) -> tuple[bool,dict[str,Any]]:
    try:
        with zipfile.ZipFile(path,"r") as z:
            names=set(z.namelist())
            required_any=("run_trace.json" in names or "reproduction.json" in names)
            detail={"path":str(path),"entries":sorted(names),"has_run_trace":"run_trace.json" in names,"has_reproduction":"reproduction.json" in names}
            if not required_any:
                return False,detail
            # Minimal structural JSON parse; actual Editor parser is the external smoke authority.
            for n in ("run_trace.json","reproduction.json"):
                if n in names:
                    try: json.loads(z.read(n).decode("utf-8"))
                    except Exception as e:
                        detail["json_error"]={"entry":n,"error":str(e)}
                        return False,detail
            return True,detail
    except Exception as e:
        return False,{"path":str(path),"error":f"{type(e).__name__}: {e}"}


def _validate_legacy_package(root: Path, vibe_root: Path|None=None) -> dict[str,Any]:
    root=Path(root).resolve(); vibe_root=Path(vibe_root).resolve() if vibe_root else None
    src=root/"source/program.ordo.yaml"
    findings=[]
    if not src.is_file():
        return {"status":"FAIL","package":str(root),"findings":[{"code":"GP_PROGRAM_SOURCE_MISSING","path":str(src)}]}
    try:
        program=yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    except Exception as e:
        return {"status":"FAIL","package":str(root),"findings":[{"code":"GP_PROGRAM_SOURCE_INVALID_YAML","error":str(e)}]}
    if not isinstance(program,dict):
        return {"status":"FAIL","package":str(root),"findings":[{"code":"GP_PROGRAM_SOURCE_ROOT_NOT_MAPPING"}]}

    nodes={str(x.get("id")):x for x in (program.get("nodes") or []) if isinstance(x,dict) and x.get("id")}
    gates={str(x.get("id")):x for x in (program.get("gates") or []) if isinstance(x,dict) and x.get("id")}
    internal=set(nodes)|set(gates)
    ext=_external_terminals(program)
    all_ids=internal|ext
    adj={k:_element_targets(v,is_gate=False) for k,v in nodes.items()}
    adj.update({k:_element_targets(v,is_gate=True) for k,v in gates.items()})
    incoming={k:set() for k in all_ids}
    for source,targets in adj.items():
        for target in targets:
            if target in CANONICAL_RESERVED_ROUTE_TARGETS:
                continue
            if target not in all_ids:
                findings.append({"code":"GP_GRAPH_UNKNOWN_TARGET","element_id":source,"target":target})
            else:
                incoming.setdefault(target,set()).add(source)
    entry=((program.get("graph_contract") or {}).get("entry_node") if isinstance(program.get("graph_contract"),dict) else None)
    if not entry:
        entry=((program.get("playbook") or {}).get("entry_node") if isinstance(program.get("playbook"),dict) else None)
    if entry and entry not in all_ids:
        findings.append({"code":"GP_GRAPH_UNKNOWN_TARGET","element_id":"$entry","target":entry})
    seen=set(); stack=[entry] if entry else []
    while stack:
        cur=stack.pop()
        if cur in seen or cur not in all_ids: continue
        seen.add(cur)
        stack.extend(t for t in adj.get(cur,[]) if t in all_ids)
    for eid in sorted(internal-seen):
        findings.append({"code":"GP_GRAPH_UNREACHABLE_ELEMENT","element_id":eid,"entry":entry})
    for term in sorted(ext):
        if not incoming.get(term):
            findings.append({"code":"GP_GRAPH_TERMINAL_NO_INCOMING","terminal":term})
        elif entry and term not in seen:
            findings.append({"code":"GP_GRAPH_TERMINAL_NO_INCOMING","terminal":term,"reason":"incoming_not_reachable_from_entry"})

    # Effective ownership and response contract.
    for nid,node in nodes.items():
        owner=_owner(node)
        node_strings=list(_strings(node))
        if owner=="model":
            human_shape=bool(node.get("question")) and bool(node.get("answer_type"))
            answer_ref=any("$answer" in s for s in node_strings)
            if human_shape or answer_ref:
                findings.append({"code":"GP_EFFECTIVE_OWNERSHIP_CONFLICT","element_id":nid,
                                 "declared_owner":owner,"human_shape":human_shape,"answer_ref":answer_ref})
            mrc=node.get("model_result_contract")
            if isinstance(mrc,dict) and mrc.get("required_state_writes"):
                req={str(x) for x in mrc.get("required_state_writes") or []}
                auth=node.get("authority_contract") or {}
                covered=set()
                if isinstance(auth,dict):
                    if isinstance(auth.get("required_state_writes"),list): covered.update(str(x) for x in auth["required_state_writes"])
                    if isinstance(auth.get("derived_targets"),dict): covered.update(str(x) for x in auth["derived_targets"].keys())
                    if isinstance(auth.get("confirmed_targets"),dict): covered.update(str(x) for x in auth["confirmed_targets"].keys())
                if not req <= covered:
                    findings.append({"code":"GP_MODEL_REQUIRED_WRITES_UNENFORCED","element_id":nid,
                                     "required":sorted(req),"runtime_enforced":sorted(covered),"missing":sorted(req-covered)})
        if owner=="human":
            # Direct response may store full verbatim $answer, but structured selectors require model interpretation in observed Editor runtime.
            structured=[]
            for path,value in _walk(node.get("on_answer")):
                if isinstance(value,str) and re.search(r"\$answer\.[A-Za-z0-9_]",value):
                    structured.append({"path":path,"value":value})
            if structured:
                findings.append({"code":"GP_HUMAN_AUTHORITY_MODEL_INTERPRETATION","element_id":nid,"selectors":structured})

    # Package-tool transport: fail on raw canonical state in argv/purpose rather than short materialized context paths.
    for nid,node in nodes.items():
        ec=node.get("execution_contract") or {}
        is_tool=_owner(node)=="deterministic" and (str(ec.get("runtime_executor") or "").casefold()=="package_tool" or str(node.get("action") or "").upper().startswith("PACKAGE."))
        if not is_tool: continue
        bad=[]
        for path,value in _walk({k:node.get(k) for k in ("args","argv","command","purpose") if k in node}):
            if isinstance(value,str) and re.search(r"(?:\{?\$state\.|\{\{?state\.)",value): bad.append({"path":path,"value":value})
        if bad:
            findings.append({"code":"GP_PACKAGE_TOOL_RAW_STATE_ARGV","element_id":nid,"references":bad})

    # RUN -> evidence -> separate GATE contract.
    for nid,node in nodes.items():
        if not _is_validation_run(node): continue
        targets=adj.get(nid,[])
        branched=False
        oa=node.get("on_answer")
        if isinstance(oa,dict):
            branch_keys=[k for k in oa if k not in {"next","update_state"}]
            branched=bool(branch_keys)
        gate_targets=[t for t in targets if t in gates]
        updates=_all_update_state(node)
        evidence_keys=[k for k in updates if "evidence" in str(k).casefold() or "report" in str(k).casefold()]
        if branched or len(gate_targets)!=1:
            findings.append({"code":"GP_RUN_GATE_CONFLATION","element_id":nid,"targets":targets,"gate_targets":gate_targets,"branched":branched})
        elif not evidence_keys:
            # Artifact evidence is also acceptable when materialized explicitly.
            art=node.get("artifact") or {}
            has_artifact=isinstance(art,dict) and bool(art.get("expected_path"))
            if not has_artifact:
                findings.append({"code":"GP_RUN_GATE_CONFLATION","element_id":nid,"reason":"run_has_no_materialized_evidence","gate":gate_targets[0]})

    # Declared output control-flow materialization.
    reachable_records={eid:nodes[eid] for eid in nodes if eid in seen}
    materialized_paths=set()
    materialized_ids=set()
    for nid,node in reachable_records.items():
        action=str(node.get("action") or "").upper()
        art=node.get("artifact") or {}
        out=node.get("output")
        if action.startswith(("DOCUMENT.","PACKAGE.")) or isinstance(art,dict):
            if isinstance(out,str): materialized_paths.add(out)
            if isinstance(art,dict) and isinstance(art.get("expected_path"),str): materialized_paths.add(art["expected_path"])
            if isinstance(art,dict) and isinstance(art.get("artifact_id"),str): materialized_ids.add(art["artifact_id"])
    for o in program.get("outputs") or []:
        if not isinstance(o,dict): continue
        oid=str(o.get("id") or "")
        opath=str(o.get("path") or o.get("output") or o.get("expected_path") or "")
        allowed_after=[str(x) for x in (o.get("allowed_after") or []) if isinstance(x,str)]
        explicit_reachable=bool(allowed_after) and all(x in seen for x in allowed_after)
        if (opath and opath not in materialized_paths) and (not oid or oid not in materialized_ids) and not explicit_reachable:
            findings.append({"code":"GP_ARTIFACT_NOT_ON_CONTROL_FLOW","artifact_id":oid or None,"path":opath or None})
        elif not opath and oid and oid not in materialized_ids and not explicit_reachable:
            findings.append({"code":"GP_ARTIFACT_NOT_ON_CONTROL_FLOW","artifact_id":oid,"path":None})

    # Auto Answers / replay package shape, if present in candidate.
    for replay in [root/"EDITOR_AUTO_ANSWERS.zip", root/"generated_outputs/EDITOR_AUTO_ANSWERS.zip"]:
        if replay.is_file():
            ok,detail=_replay_zip_status(replay)
            if not ok: findings.append({"code":"GP_AUTO_ANSWERS_REPLAY_INVALID",**detail})

    # Source-only packaging law.
    for p in root.rglob("*.json"):
        rel=p.relative_to(root).as_posix().casefold()
        if any(rel.endswith(pattern) for pattern in EDITOR_COMPILED_PATTERNS):
            findings.append({"code":"GP_EDITOR_COMPILED_ARTIFACT_PACKAGED","path":p.relative_to(root).as_posix()})

    # Free-text retry loops must mutate progress state when the retry path after capture is purely deterministic.
    # If a model-owned semantic repair step sits in the loop, repeated input can legitimately produce a changed semantic state,
    # so this specific no_progress-cycle rule is not applied mechanically.
    def deterministic_retry_gates(start: str, max_depth: int=8) -> set[str]:
        q=deque([(start,0,False)]); seen_local=set(); gs=set()
        while q:
            cur,d,model_seen=q.popleft()
            key=(cur,d,model_seen)
            if key in seen_local or d>max_depth: continue
            seen_local.add(key)
            if cur in gates:
                fail_targets=[]
                for k in ("on_fail","fail_to"):
                    fail_targets.extend(_route_targets(gates[cur].get(k)))
                if start in fail_targets and not model_seen:
                    gs.add(cur)
                continue
            if cur != start and cur in nodes and _owner(nodes[cur])=="model":
                model_seen=True
            for t in adj.get(cur,[]):
                if t in internal: q.append((t,d+1,model_seen))
        return gs
    for nid,node in nodes.items():
        if _owner(node)!="human" or str(node.get("answer_type") or "").casefold()!="free_text": continue
        retry_gates=deterministic_retry_gates(nid)
        if retry_gates:
            updates=_all_update_state(node)
            progress=[k for k,v in updates.items() if re.search(r"attempt|retry|timestamp|progress|submitted_at|attempted_at",str(k),re.I)
                      or (isinstance(v,str) and "$runtime.timestamp" in v)]
            if not progress:
                findings.append({"code":"GP_FREE_TEXT_RETRY_NO_PROGRESS","element_id":nid,"retry_gates":sorted(retry_gates)})

    codes=sorted({x["code"] for x in findings})
    return {
        "schema_version":"1.0",
        "validator_id":"VIBE_GENERATED_PLAYBOOK_CONTRACT_V1",
        "status":"PASS" if not findings else "FAIL",
        "package":str(root),
        "source":str(src),
        "summary":{"nodes":len(nodes),"gates":len(gates),"external_terminals":len(ext),"findings":len(findings),"codes":codes},
        "findings":findings,
    }



STATUS_VALUES={"PASS","ORDO_INVALID","ORDO_VALID_VIBE_PROFILE_NONCONFORMANT","ORDO_VALID_ADAPTER_INCOMPATIBLE","AUTO_ANSWERS_INVALID"}
LANGUAGE_CODES={
 "GP_PROGRAM_SOURCE_MISSING","GP_PROGRAM_SOURCE_INVALID_YAML","GP_PROGRAM_SOURCE_ROOT_NOT_MAPPING",
 "GP_GRAPH_UNKNOWN_TARGET","GP_GRAPH_UNREACHABLE_ELEMENT","GP_GRAPH_TERMINAL_NO_INCOMING"
}
VIBE_PROFILE_CODES={"GP_MODEL_REQUIRED_WRITES_UNENFORCED","GP_RUN_GATE_CONFLATION","GP_ARTIFACT_NOT_ON_CONTROL_FLOW"}
AUTO_ANSWERS_CODES={"GP_AUTO_ANSWERS_REPLAY_INVALID","GP_FREE_TEXT_RETRY_NO_PROGRESS"}
EDITOR_ADAPTER_CODES={"GP_EFFECTIVE_OWNERSHIP_CONFLICT","GP_HUMAN_AUTHORITY_MODEL_INTERPRETATION","GP_PACKAGE_TOOL_RAW_STATE_ARGV","GP_EDITOR_COMPILED_ARTIFACT_PACKAGED"}

def _layer_result(name:str, findings:list[dict[str,Any]], failure_status:str)->dict[str,Any]:
    return {"layer":name,"status":"PASS" if not findings else failure_status,"findings":findings,
            "summary":{"findings":len(findings),"codes":sorted({x.get('code') for x in findings if x.get('code')})}}

def validate_package_layers(root: Path, vibe_root: Path|None=None) -> dict[str,Any]:
    """Evaluate one source package without allowing a runtime adapter to redefine Ordo validity."""
    legacy=_validate_legacy_package(root,vibe_root)
    all_findings=list(legacy.get("findings") or [])
    language=[x for x in all_findings if x.get("code") in LANGUAGE_CODES]
    profile=[x for x in all_findings if x.get("code") in VIBE_PROFILE_CODES]
    auto=[x for x in all_findings if x.get("code") in AUTO_ANSWERS_CODES]
    editor=[x for x in all_findings if x.get("code") in EDITOR_ADAPTER_CODES]
    known=LANGUAGE_CODES|VIBE_PROFILE_CODES|AUTO_ANSWERS_CODES|EDITOR_ADAPTER_CODES
    unknown=[x for x in all_findings if x.get("code") not in known]
    # Unknown validator findings are treated conservatively as Vibe-profile findings, never silently promoted to language truth.
    profile.extend(unknown)
    layers={
      "language_conformance":_layer_result("ORDO_LANGUAGE_CONFORMANCE",language,"ORDO_INVALID"),
      "vibe_authoring_profile":_layer_result("VIBE_AUTHORING_PROFILE",profile,"ORDO_VALID_VIBE_PROFILE_NONCONFORMANT"),
      "auto_answers":_layer_result("AUTO_ANSWERS",auto,"AUTO_ANSWERS_INVALID"),
      "editor_dev_adapter":_layer_result("EDITOR_DEV_ADAPTER",editor,"ORDO_VALID_ADAPTER_INCOMPATIBLE"),
    }
    if language: overall="ORDO_INVALID"
    elif profile: overall="PROFILE_NONCONFORMANT"
    elif auto: overall="AUTO_ANSWERS_INVALID"
    elif editor: overall="ADAPTER_INCOMPATIBLE"
    else: overall="PASS"
    return {"schema_version":"2.0","validator_id":"VIBE_GENERATED_PLAYBOOK_LAYERED_CONTRACT_V2",
            "semantic_source_of_truth":"canonical_ordo_language","overall_status":overall,
            "package":str(Path(root).resolve()),**layers,
            "legacy_findings_count":len(all_findings)}

def validate_package(root: Path, vibe_root: Path|None=None, target: str="language_core") -> dict[str,Any]:
    """Compatibility API. target selects which authority layers block this verification check."""
    r=validate_package_layers(root,vibe_root)
    target=str(target or "language_core")
    selected=[r["language_conformance"]]
    if target in {"vibe_authoring","chat_internal","editor_dev","full"}:
        selected.append(r["vibe_authoring_profile"])
    if target in {"editor_dev","full"}:
        selected += [r["auto_answers"],r["editor_dev_adapter"]]
    elif target=="auto_answers":
        selected=[r["auto_answers"]]
    blocking=[x for x in selected if x["status"]!="PASS"]
    status="PASS" if not blocking else blocking[0]["status"]
    return {"schema_version":"2.0","validator_id":"VIBE_GENERATED_PLAYBOOK_TARGET_CONTRACT_V2","target":target,
            "status":status,"semantic_source_of_truth":"canonical_ordo_language",
            "selected_layers":[x["layer"] for x in selected],"blocking":blocking,"layers":r}

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("package",nargs="?",default=".")
    ap.add_argument("--vibe-root",default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--report")
    ap.add_argument("--target",default="language_core",choices=["language_core","vibe_authoring","chat_internal","auto_answers","editor_dev","full"])
    a=ap.parse_args()
    result=validate_package(Path(a.package),Path(a.vibe_root),target=a.target)
    if a.report:
        p=Path(a.report)
        if not p.is_absolute(): p=Path(a.package)/p
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["status"]=="PASS" else 1

if __name__=="__main__": raise SystemExit(main())
