from __future__ import annotations
import json, os, shutil, subprocess, tempfile, time, zipfile, io, sys, hashlib, mimetypes
from pathlib import Path
from typing import Any, Callable
import re

HERE = Path(__file__).resolve().parent
CHECKS_DIR = HERE / "checks"
TOOLKIT_DIR = HERE / "toolkit"

def load_catalog() -> list[dict[str, Any]]:
    rows=[]
    for path in sorted(CHECKS_DIR.glob("*.json")):
        try:
            item=json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append({"id":path.stem,"title":path.stem,"group":"registry","order":9999,"enabled":False,"registry_error":str(exc)})
            continue
        item["descriptor_file"]=path.name
        rows.append(item)
    return sorted(rows,key=lambda x:(int(x.get("order",9999)),str(x.get("id",""))))

def _package_root(extract_root: Path, source_name: str) -> Path:
    source_name=str(source_name or "").replace("\\","/").strip("/")
    if source_name:
        source=(extract_root/source_name)
        candidate=source.parent
        if candidate.name.lower() in {"source","src","playbook"} and candidate.parent.exists():
            candidate=candidate.parent
        if candidate.exists(): return candidate
    children=[p for p in extract_root.iterdir() if p.is_dir()]
    files=[p for p in extract_root.iterdir() if p.is_file()]
    if len(children)==1 and not files: return children[0]
    return extract_root

def _expand(tokens:list[str], ctx:dict[str,str])->list[str]:
    return [str(t).format(**ctx) for t in tokens]

def _normalize_command(tokens:list[str])->list[str]:
    """Resolve portable symbolic executables in verification descriptors.

    Descriptors are part of the language/tooling package and must not assume that
    a binary named `python` or `python3` is present on PATH. They run inside the
    Editor process environment, so Python commands are normalized to the exact
    interpreter currently running the Editor.
    """
    if not tokens:
        return []
    cmd=list(tokens)
    head=str(cmd[0]).strip()
    if head in {"python", "python3", "{python}"}:
        cmd[0]=sys.executable
    return cmd

def _skip_kind(item:dict[str,Any], reason:str)->tuple[str,str]:
    explicit=str(item.get("skip_kind") or "").strip().lower().replace("-","_")
    labels={
        "not_applicable":"Not applicable",
        "needs_runtime_evidence":"Needs runtime evidence",
        "needs_selected_gate":"Needs selected gate",
        "needs_bindings_context":"Needs bindings context",
        "needs_template_context":"Needs template context",
        "needs_tree_module_context":"Needs tree-module context",
        "release_only":"Release-only",
        "toolkit_only":"Toolkit-only",
        "unsafe_one_click":"Not in safe one-click",
        "missing_required_context":"Needs additional context",
        "missing_optional_dependency":"Missing optional dependency",
    }
    if explicit in labels:
        return explicit,labels[explicit]
    text=(str(reason or "")+" "+str(item.get("description") or "")+" "+str(item.get("id") or "")).lower()
    if "runtime state" in text or "journey evidence" in text or "intake evidence" in text:
        return "needs_runtime_evidence",labels["needs_runtime_evidence"]
    if "gate_id" in text or "gate-specific" in text:
        return "needs_selected_gate",labels["needs_selected_gate"]
    if "bindings" in text:
        return "needs_bindings_context",labels["needs_bindings_context"]
    if "template" in text and ("contract" in text or "registry" in text or "rendered" in text):
        return "needs_template_context",labels["needs_template_context"]
    if "tree-module" in text or "tree module" in text:
        return "needs_tree_module_context",labels["needs_tree_module_context"]
    if "release" in text and ("not applicable" in text or "release artifacts" in text):
        return "release_only",labels["release_only"]
    if "portable authoring bundle" in text or "toolkit" in text:
        return "toolkit_only",labels["toolkit_only"]
    if "safe one-click" in text:
        return "unsafe_one_click",labels["unsafe_one_click"]
    if "not applicable" in text:
        return "not_applicable",labels["not_applicable"]
    return "missing_required_context",labels["missing_required_context"]


def _applicable(item:dict[str,Any], package_root:Path, source_path:Path|None)->tuple[bool,str]:
    if not item.get("enabled",True): return False,str(item.get("skip_reason") or "Disabled in verification registry.")
    req=item.get("requires") or []
    if "gate_id" in req: return False,"Requires a concrete gate_id; run it from a gate-specific context."
    if "bindings_file" in req: return False,"Requires a document-field bindings file."
    if "prompt_compilation" in req: return False,"Requires an existing prompt-only compilation directory and source binding."
    if "template_contract" in req: return False,"Requires a concrete template contract."
    if "template_registry" in req: return False,"Requires a concrete Template Registry."
    if "tree_instance" in req: return False,"Requires a concrete reusable tree-module instance."
    if "rendered_artifact" in req: return False,"Requires a concrete rendered template artifact."
    if "template_contract_pair" in req: return False,"Requires old and new template contracts."
    if "release_context" in req: return False,"Creates/validates release artifacts and is not part of the safe one-click playbook suite."
    if "portable_bundle" in req: return False,"Validates the Vibe portable authoring bundle itself, not the loaded playbook."
    if "source_file" in req and source_path is None: return False,"Could not resolve the package source file."
    for executable in item.get("requires_executables") or []:
        executable=str(executable or "").strip()
        if executable and shutil.which(executable) is None:
            return False,f"Optional verification dependency `{executable}` is not installed in the Editor environment."
    for rel in item.get("requires_any_files") or []:
        if not any(package_root.glob(rel)): return False,f"Not applicable: no file matches {rel}."
    evidence=item.get("evidence_requirement") if isinstance(item.get("evidence_requirement"),dict) else None
    if evidence:
        matches=[]
        for rel in evidence.get("any_of") or []:
            matches.extend(package_root.glob(str(rel)))
        if evidence.get("require_nonempty"):
            matches=[p for p in matches if p.is_file() and p.stat().st_size>0]
            # For a journey YAML, an empty events list is still no runtime evidence.
            filtered=[]
            for path in matches:
                if path.suffix.lower() in {".yaml",".yml"}:
                    try:
                        import yaml
                        data=yaml.safe_load(path.read_text(encoding="utf-8"))
                        if isinstance(data,dict) and isinstance(data.get("events"),list) and len(data.get("events") or [])==0:
                            continue
                    except Exception:
                        pass
                filtered.append(path)
            matches=filtered
        if not matches:
            return False,str(evidence.get("skip_reason") or "Required runtime evidence is not available.")
    return True,""


def _sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def _read_evidence_file(path:Path)->dict[str,Any]:
    media=mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    item={"path":path.as_posix(),"name":path.name,"media_type":media,"size_bytes":path.stat().st_size,"sha256":_sha256_file(path)}
    if path.stat().st_size>2_000_000:
        item["content_omitted"]="file_too_large"
        return item
    try:
        text=path.read_text(encoding="utf-8")
    except Exception:
        item["content_omitted"]="binary_or_non_utf8"
        return item
    if path.suffix.lower()==".json":
        try:item["content_json"]=json.loads(text)
        except Exception:item["content_text"]=text
    else:
        item["content_text"]=text
    return item

def _report_snapshot(package_root:Path)->dict[str,tuple[int,int]]:
    snap={}
    candidates=[]
    reports=package_root/"reports"
    runtime=package_root/"runtime"
    if reports.exists(): candidates.extend([p for p in reports.rglob("*") if p.is_file()])
    if runtime.exists(): candidates.extend([p for p in runtime.rglob("*") if p.is_file() and ("report" in p.name.lower() or "validation" in p.name.lower())])
    for path in candidates:
        try:snap[str(path.resolve())]=(path.stat().st_mtime_ns,path.stat().st_size)
        except Exception:pass
    return snap

def _collect_generated_evidence(package_root:Path,before:dict[str,tuple[int,int]],output:str)->list[dict[str,Any]]:
    candidates:set[Path]=set()
    after=_report_snapshot(package_root)
    for raw,meta in after.items():
        if raw not in before or before.get(raw)!=meta:
            candidates.add(Path(raw))
    # Also honor concrete report paths emitted by the tool even when pre-existing.
    for token in re.findall(r'(?P<path>(?:/[^\\s()]+|[-A-Za-z0-9_./]+\\.(?:json|ya?ml|md|txt)))',str(output or "")):
        clean=token.rstrip(".,;:")
        path=Path(clean)
        if not path.is_absolute(): path=package_root/path
        try:
            resolved=path.resolve()
            resolved.relative_to(package_root.resolve())
        except Exception:
            continue
        if resolved.exists() and resolved.is_file():
            candidates.add(resolved)
    out=[]
    for path in sorted(candidates,key=lambda x:str(x)):
        try:
            item=_read_evidence_file(path)
            item["path"]=str(path.resolve().relative_to(package_root.resolve())).replace("\\\\","/")
            out.append(item)
        except Exception:
            pass
    return out


def _evidence_summary(evidence:list[dict[str,Any]])->str:
    parts=[]
    for item in evidence:
        data=item.get("content_json")
        if not isinstance(data,dict):
            continue
        status=data.get("status") or data.get("go_no_go") or data.get("cli_status")
        if status:
            parts.append(f"{item.get('path')}: status={status}")
        problems=[]
        for key in ("errors","issues","blocking_issues","violations","warnings"):
            rows=data.get(key)
            if isinstance(rows,list):
                for row in rows[:4]:
                    if isinstance(row,dict):
                        code=row.get("code") or row.get("step") or key.rstrip("s")
                        message=row.get("message") or row.get("reason") or row.get("summary")
                        if message: problems.append(f"{code}: {message}")
                    elif row:
                        problems.append(str(row))
        if problems:
            parts.extend(problems[:6])
        summary=data.get("summary")
        if isinstance(summary,dict) and not problems:
            compact=", ".join(f"{k}={v}" for k,v in list(summary.items())[:6] if isinstance(v,(str,int,float,bool)) or v is None)
            if compact: parts.append(compact)
    return " · ".join(parts[:8])


def run_catalog(*, raw_zip:bytes, source_name:str, progress:Callable[[dict[str,Any]],None], internal_editor_validate:Callable[[Path],dict[str,Any]]|None=None) -> dict[str,Any]:
    catalog=load_catalog(); started=time.time(); summary={"PASS":0,"FAIL":0,"SKIPPED":0,"ERROR":0}
    with tempfile.TemporaryDirectory(prefix="ordo_editor_verify_") as td:
        extract_root=Path(td)/"package"; extract_root.mkdir()
        with zipfile.ZipFile(io.BytesIO(raw_zip),"r") as z: z.extractall(extract_root)
        package_root=_package_root(extract_root,source_name)
        source_path=(extract_root/source_name) if source_name and (extract_root/source_name).exists() else None
        out_root=Path(td)/"verification_outputs"; out_root.mkdir()
        ctx={"package_root":str(package_root),"source_path":str(source_path or ""),"output_root":str(out_root),"toolkit_root":str(TOOLKIT_DIR)}
        env=os.environ.copy(); env["PYTHONPATH"]=str(TOOLKIT_DIR/"ordo_pkg") + (os.pathsep+env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
        total=len(catalog)
        for index,item in enumerate(catalog,1):
            base={"id":item.get("id"),"title":item.get("title"),"group":item.get("group"),"description":item.get("description",""),"index":index,"total":total}
            ok,reason=_applicable(item,package_root,source_path)
            if not ok:
                skip_kind,skip_label=_skip_kind(item,reason); result={**base,"status":"SKIPPED","message":reason,"skip_kind":skip_kind,"skip_label":skip_label,"duration_ms":0,"exit_code":None,"output":"","evidence_summary":"","evidence":[]}; summary["SKIPPED"]+=1; progress(result); continue
            progress({**base,"status":"RUNNING","message":"Running…"})
            t0=time.time()
            before_reports=_report_snapshot(package_root)
            try:
                runner=item.get("runner") or {}; rtype=runner.get("type","command")
                if rtype=="internal_editor_validate":
                    if internal_editor_validate is None: raise RuntimeError("Current Editor validation callback is unavailable.")
                    info=internal_editor_validate(source_path or package_root)
                    status="PASS" if str(info.get("status") or "").upper() in {"PASS","PASSED"} else "FAIL"
                    output=json.dumps(info,ensure_ascii=False,indent=2)
                    code=0 if status=="PASS" else 1
                else:
                    cmd=_normalize_command(_expand(list(runner.get("command") or []),ctx))
                    if not cmd: raise RuntimeError("Verification descriptor has no command.")
                    timeout=int(item.get("timeout_seconds") or 120)
                    cp=subprocess.run(cmd,cwd=str(package_root),env=env,capture_output=True,text=True,timeout=timeout)
                    code=cp.returncode; output=(cp.stdout or "") + (("\n"+cp.stderr) if cp.stderr else "")
                    status="PASS" if code==0 else "FAIL"
                msg=(output.strip().splitlines()[-1] if output.strip() else ("Completed." if code==0 else "Failed."))
                evidence=_collect_generated_evidence(package_root,before_reports,output)
                evidence_summary=_evidence_summary(evidence)
                result={**base,"status":status,"message":msg[:500],"exit_code":code,"duration_ms":round((time.time()-t0)*1000),"output":output[-20000:],"evidence":evidence,"evidence_summary":evidence_summary}
                summary[status]+=1
            except subprocess.TimeoutExpired as exc:
                result={**base,"status":"ERROR","message":f"Timed out after {exc.timeout}s.","duration_ms":round((time.time()-t0)*1000),"output":""}; summary["ERROR"]+=1
            except Exception as exc:
                result={**base,"status":"ERROR","message":str(exc),"duration_ms":round((time.time()-t0)*1000),"output":""}; summary["ERROR"]+=1
            progress(result)
    overall="PASS" if summary["FAIL"]==0 and summary["ERROR"]==0 else "FAIL"
    return {"status":overall,"summary":summary,"duration_ms":round((time.time()-started)*1000),"total":len(catalog)}
