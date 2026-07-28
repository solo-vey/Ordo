#!/usr/bin/env python3
import argparse, hashlib, yaml
from pathlib import Path

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--declarations", required=True)
    ap.add_argument("--base-dir", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    data = yaml.safe_load(Path(args.declarations).read_text(encoding="utf-8"))
    findings = []
    allowed = {"archive_digest", "content_tree_digest", "source_digest", "embedded_file_digest"}

    for item in data.get("checksums", []):
        domain = item.get("domain")
        target = item.get("target")
        declared = item.get("sha256")
        if domain not in allowed:
            findings.append({"code": "unknown_checksum_domain", "target": target, "blocking": True})
            continue
        if not target:
            findings.append({"code": "ambiguous_digest_target", "blocking": True})
            continue
        path = Path(args.base_dir) / target
        if not path.exists():
            findings.append({"code": "target_missing", "target": target, "blocking": True})
            continue
        actual = digest(path)
        if declared != actual:
            findings.append({
                "code": "declared_actual_digest_mismatch",
                "target": target,
                "declared": declared,
                "actual": actual,
                "blocking": True
            })

    out = {
        "schema": "ordo.prh.checksum_domain_report.v1",
        "findings": findings,
        "verdict": "FAIL" if any(f["blocking"] for f in findings) else "PASS",
    }
    Path(args.output).write_text(yaml.safe_dump(out, sort_keys=False), encoding="utf-8")

if __name__ == "__main__":
    main()
