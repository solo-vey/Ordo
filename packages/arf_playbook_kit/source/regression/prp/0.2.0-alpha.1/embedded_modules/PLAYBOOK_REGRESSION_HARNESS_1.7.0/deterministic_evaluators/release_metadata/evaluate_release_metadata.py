#!/usr/bin/env python3
import argparse, json, re, yaml
from pathlib import Path

def load(path):
    p = Path(path)
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8")
    if p.suffix == ".json":
        return json.loads(text)
    if p.suffix in (".yaml", ".yml"):
        return yaml.safe_load(text)
    return {"text": text}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--release", required=True)
    ap.add_argument("--archive-name", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    manifest = load(args.manifest)
    release = load(args.release)
    findings = []

    mv = manifest.get("version") or manifest.get("playbook", {}).get("version")
    rv = release.get("version")
    if mv and rv and mv != rv:
        findings.append({"code": "release_manifest_identity_conflict", "blocking": True})

    filename_versions = re.findall(r'\d+\.\d+\.\d+(?:[-._]?[A-Za-z0-9]+)?', args.archive_name)
    if mv and filename_versions and not any(mv.replace("-", "_") in v.replace("-", "_") for v in filename_versions):
        findings.append({"code": "version_identity_mismatch", "blocking": True})

    ms = manifest.get("status")
    rs = release.get("release_status")
    canonical_claim = release.get("canonical_claim")
    if (ms == "candidate" or rs == "candidate") and canonical_claim is True:
        findings.append({"code": "candidate_canonical_status_conflict", "blocking": True})

    out = {
        "schema": "ordo.prh.release_metadata_report.v1",
        "findings": findings,
        "verdict": "FAIL" if any(f["blocking"] for f in findings) else "PASS",
    }
    Path(args.output).write_text(yaml.safe_dump(out, sort_keys=False), encoding="utf-8")

if __name__ == "__main__":
    main()
