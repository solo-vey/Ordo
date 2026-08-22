#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
import yaml
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("target",nargs="?",default=None)
    ap.add_argument("--vibe-root",default=str(Path(__file__).resolve().parents[1]))
    a=ap.parse_args()
    vr=Path(a.vibe_root).resolve()
    canonical=vr/"PLAYBOOK_LAWS.md"
    guide=vr/"canonical_support/guides/PLAYBOOK_LAWS.md"
    templ=vr/"canonical_support/output_templates/PLAYBOOK_LAWS.md"
    target=Path(a.target).resolve()/"PLAYBOOK_LAWS.md" if a.target else canonical
    source=vr/"source/program.ordo.yaml"
    checks={k:p.is_file() for k,p in {
        "canonical_root_present":canonical,"guide_present":guide,"template_present":templ,
        "target_present":target,"source_present":source}.items()}
    if all(checks.values()):
        h={sha(canonical),sha(guide),sha(templ)}
        checks["canonical_copies_match"]=len(h)==1
        checks["target_matches_canonical"]=sha(target)==sha(canonical)
        doc=yaml.safe_load(source.read_text(encoding="utf-8")) or {}
        laws=((doc.get("playbook_laws") or {}).get("laws") or [])
        text=canonical.read_text(encoding="utf-8")
        missing=[]
        for law in laws:
            lid=str(law.get("id") or "")
            ltext=str(law.get("text") or "")
            if lid not in text or ltext not in text:
                missing.append(lid or "<missing-id>")
        checks["source_laws_materialized_verbatim"]=not missing
    else:
        missing=[]
    status="PASS" if checks and all(checks.values()) else "FAIL"
    print(json.dumps({"status":status,"checks":checks,
                      "canonical_sha256":sha(canonical) if canonical.is_file() else None,
                      "target":str(target),"missing_source_laws":missing},indent=2))
    raise SystemExit(0 if status=="PASS" else 1)
if __name__=="__main__": main()
