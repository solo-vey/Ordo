#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
import yaml

MODES={"template","assembler"}

def inside(root,p):
    try: Path(p).resolve().relative_to(Path(root).resolve()); return True
    except Exception: return False

def validate_package(root: Path, registry_rel="verification/ARTIFACT_MATERIALIZATION_REGISTRY.json"):
    root=Path(root).resolve()
    src=root/"source/program.ordo.yaml"
    regp=root/registry_rel
    findings=[]
    if not src.is_file(): findings.append({"code":"PROGRAM_SOURCE_MISSING","path":str(src)})
    if not regp.is_file(): findings.append({"code":"ARTIFACT_REGISTRY_MISSING","path":str(regp)})
    if findings:
        return {"status":"FAIL","findings":findings}
    program=yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    declared={o.get("id"):o for o in (program.get("outputs") or []) if isinstance(o,dict) and o.get("id")}
    try: reg=json.loads(regp.read_text(encoding="utf-8"))
    except Exception as e:
        return {"status":"FAIL","findings":[{"code":"ARTIFACT_REGISTRY_INVALID_JSON","error":str(e)}]}
    artifacts=reg.get("artifacts"); artifacts=artifacts if isinstance(artifacts,list) else []
    by_id={}
    for i,a in enumerate(artifacts):
        if not isinstance(a,dict):
            findings.append({"code":"ARTIFACT_ENTRY_NOT_OBJECT","index":i}); continue
        aid=a.get("artifact_id")
        if not aid:
            findings.append({"code":"ARTIFACT_ID_REQUIRED","index":i}); continue
        if aid in by_id: findings.append({"code":"DUPLICATE_ARTIFACT_ID","artifact_id":aid})
        by_id[aid]=a
        if aid not in declared:
            findings.append({"code":"UNDECLARED_ARTIFACT","artifact_id":aid})
        mode=a.get("materialization_mode")
        if mode not in MODES:
            findings.append({"code":"INVALID_MATERIALIZATION_MODE","artifact_id":aid,"mode":mode}); continue
        if not str(a.get("output_path") or "").strip():
            findings.append({"code":"OUTPUT_PATH_REQUIRED","artifact_id":aid})
        cc=a.get("content_contract")
        if not isinstance(cc,dict) or not cc:
            findings.append({"code":"CONTENT_CONTRACT_REQUIRED","artifact_id":aid})
        if not isinstance(a.get("validators"),list) or not a.get("validators"):
            findings.append({"code":"VALIDATOR_BINDING_REQUIRED","artifact_id":aid})
        if a.get("post_materialization_validation_required") is not True:
            findings.append({"code":"POST_MATERIALIZATION_VALIDATION_REQUIRED","artifact_id":aid})
        ref=None
        if mode=="template":
            ref=a.get("template_path")
            if not ref: findings.append({"code":"TEMPLATE_PATH_REQUIRED","artifact_id":aid})
        elif mode=="assembler":
            ref=a.get("assembler_ref")
            if not ref: findings.append({"code":"ASSEMBLER_REF_REQUIRED","artifact_id":aid})
        if ref:
            pp=(root/str(ref)).resolve()
            if not inside(root,pp):
                findings.append({"code":"MATERIALIZER_REF_OUTSIDE_PACKAGE","artifact_id":aid,"ref":ref})
            elif not pp.is_file():
                findings.append({"code":"MATERIALIZER_REF_MISSING","artifact_id":aid,"ref":ref})
    for aid in declared:
        if aid not in by_id:
            findings.append({"code":"DECLARED_OUTPUT_WITHOUT_MATERIALIZATION_CONTRACT","artifact_id":aid})
    status="PASS" if not findings else "FAIL"
    return {"status":status,"declared_outputs":sorted(declared),"registry_artifacts":sorted(by_id),
            "findings":findings}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("package",nargs="?",default=".")
    ap.add_argument("--registry",default="verification/ARTIFACT_MATERIALIZATION_REGISTRY.json")
    a=ap.parse_args()
    result=validate_package(Path(a.package),a.registry)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["status"]=="PASS" else 1

if __name__=="__main__": raise SystemExit(main())
