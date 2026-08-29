#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main(paths):
    runs = []
    seen = set()
    errors = []
    for p in paths:
        root = Path(p)
        for f in root.rglob("run_manifest.json"):
            data = json.loads(f.read_text(encoding="utf-8"))
            rid = data.get("run_id")
            if rid in seen:
                errors.append(f"duplicate run_id: {rid}")
            seen.add(rid)
            runs.append(data)
    out = {
        "run_count": len(runs),
        "unique_run_count": len(seen),
        "errors": errors,
        "by_chat": {},
        "by_model_label": {}
    }
    for r in runs:
        out["by_chat"].setdefault(r["chat_id"], 0)
        out["by_chat"][r["chat_id"]] += 1
        out["by_model_label"].setdefault(r["declared_model_label"], 0)
        out["by_model_label"][r["declared_model_label"]] += 1
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
