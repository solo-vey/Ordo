from __future__ import annotations

import importlib.util
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
EDITOR = ROOT / "utilities" / "ordo_tree_editor" / "editor_service.py"

if not EDITOR.is_file():
    print("PASS: base Vibe ARF intentionally has no embedded Tree Editor")
    raise SystemExit(0)

spec = importlib.util.spec_from_file_location("editor_service_under_test", EDITOR)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

failures = []

def check(cond, msg):
    if not cond:
        failures.append(msg)

# Production packages intentionally may omit duplicate root language/.
check(not (ROOT / "language").exists(), "fixture expects root language/ to be absent")
resolved = mod._resolve_registry_root(ROOT) if hasattr(mod, "_resolve_registry_root") else None
check(resolved == ROOT / "canonical_support", f"registry root must resolve to canonical_support, got {resolved}")

source = yaml.safe_load((ROOT / "source" / "program.ordo.yaml").read_text(encoding="utf-8"))
report = mod.validate_source(source)
registry = report.get("lint", {}).get("source_registry_check", {})
check(registry.get("status") == "passed", f"native Editor source registry must pass: {registry}")
check(registry.get("unknown") == [], f"native Editor must report zero unknown constructs: {registry.get('unknown')}")
check(report.get("graph", {}).get("status") == "passed", "native Editor graph validation must remain passed")
check(report.get("status") == "passed", f"native Editor validation must pass overall: {report.get('issues', [])[:5]}")

if failures:
    for f in failures:
        print("FAIL:", f)
    raise SystemExit(1)
print("PASS: editor registry root resolution and native validation")
