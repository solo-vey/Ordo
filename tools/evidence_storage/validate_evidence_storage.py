#!/usr/bin/env python3
"""Validate Ordo evidence storage thresholds and inventory bindings."""
from pathlib import Path
import argparse, hashlib, json, sys

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args=ap.parse_args()
    root=Path(args.root).resolve()
    inv_path=root/"manifests"/"EVIDENCE_BINARY_INVENTORY.json"
    inv=json.loads(inv_path.read_text(encoding="utf-8"))
    errors=[]
    for item in inv["artifacts"]:
        p=root/item["path"]
        if not p.exists():
            errors.append(f"missing: {item['path']}")
            continue
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != item["sha256"]:
            errors.append(f"sha256 mismatch: {item['path']}")
        size=p.stat().st_size
        if size != item["size_bytes"]:
            errors.append(f"size mismatch: {item['path']}")
        if size > 25*1024*1024 and item["storage_class"]=="git_inline":
            errors.append(f"oversize inline artifact: {item['path']}")
    if errors:
        print(json.dumps({"status":"FAIL","errors":errors},indent=2))
        return 1
    print(json.dumps({"status":"PASS","checked":len(inv["artifacts"])},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
