#!/usr/bin/env python3
"""Audit negative fixture mutations and test execution classification."""
from __future__ import annotations
import argparse, ast, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "cli" / "tests"
CLASSIFICATION = ROOT / "manifests" / "TEST_EXECUTION_CLASSIFICATION.json"


def mutation_calls(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"replace", "sub", "subn"}:
                yield node


def has_mutation_assert(source: str) -> bool:
    markers = ("assertNotEqual", "assertNotIn", "assertIn", "assert ", "assertTrue", "assertFalse")
    return any(m in source for m in markers)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    cfg = json.loads(CLASSIFICATION.read_text())
    issues = []
    serial = cfg["serial_files"]
    for name, klass in serial.items():
        if not (TESTS / name).is_file():
            issues.append(f"classified test file missing: {name}")
        if klass not in {"workspace_mutating", "workspace_reading", "performance_sensitive"}:
            issues.append(f"invalid serial class for {name}: {klass}")
    for path in sorted(TESTS.glob("test_*.py")):
        source = path.read_text()
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            issues.append(f"cannot parse {path.name}: {exc}")
            continue
        calls = list(mutation_calls(tree))
        # Conservative signal: mutation calls that are used in tests which write
        # fixtures must have at least one explicit assertion proving the mutation.
        if calls and ("write_text" in source or "write_bytes" in source) and not has_mutation_assert(source):
            issues.append(f"mutation without explicit assertion signal: {path.name}")
    report = {"schema_version":"ordo.test_fixture_safety_audit.v1", "status":"passed" if not issues else "blocked", "issues":issues}
    out = args.out
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))
    return 0 if not issues else 1

if __name__ == "__main__":
    raise SystemExit(main())
