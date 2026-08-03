#!/usr/bin/env python3
"""Validate consistency between playbook state and external contract artifacts.

This is a release-facing semantic check, intentionally separate from graph
linting and compilation.  A package is checked only when it exposes the
relevant contract surfaces; packages without those optional surfaces are
reported as skipped rather than treated as failures.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_.]*)")
PRESENT_PHRASE = re.compile(r"(.+?)\bare present(?: and non-empty)?\b", re.I | re.S)
STOP_WORDS = {
    "required", "state", "objects", "present", "non", "empty", "complete",
    "internal", "consistency", "template", "binding", "coverage", "test",
    "tests", "source", "mapping", "payload", "output", "risk", "factor",
    "passport", "model", "semantic", "calculation", "timestamps", "rendering",
    "business", "identity", "history", "policy", "update", "trigger", "logic",
    "data", "attribute", "fields", "field", "value", "values", "contract",
    "every", "current", "document", "row", "rows", "section", "sections",
}


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def registry_paths(obj: Any) -> tuple[set[str], set[str]]:
    roots: set[str] = set()
    components: set[str] = set()
    variables = obj.get("variables", []) if isinstance(obj, dict) else []
    for item in variables or []:
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            parts = item["path"].split(".")
            if parts:
                roots.add(parts[0])
                components.update(parts)
    return roots, components


def binding_data(obj: Any) -> tuple[set[str], list[tuple[str, str, str]]]:
    roots: set[str] = set()
    sources: list[tuple[str, str, str]] = []
    bindings = obj.get("bindings", {}) if isinstance(obj, dict) else {}
    if not isinstance(bindings, dict):
        return roots, sources
    for key, value in bindings.items():
        roots.add(str(key))
        source = value.get("source") if isinstance(value, dict) else value
        if isinstance(source, str) and source.startswith("state."):
            sources.append((str(key), source[6:].split(".")[0], source))
    return roots, sources


def find_registry(root: Path, configured: str) -> Path | None:
    candidate = root / configured
    if candidate.exists():
        return candidate
    registry_dir = root / "registry"
    candidates = sorted(registry_dir.glob("*.y*ml")) if registry_dir.exists() else []
    return candidates[0] if len(candidates) == 1 else None


def check_package(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    root = root.resolve()
    source = root / args.playbook
    gates_dir = root / args.gates_dir
    templates_dir = root / args.templates_dir
    registry_path = find_registry(root, args.registry)
    gate_files = sorted(gates_dir.glob("*.yaml")) + sorted(gates_dir.glob("*.yml")) if gates_dir.exists() else []
    binding_files = sorted(templates_dir.glob("*BINDINGS.y*ml")) if templates_dir.exists() else []
    template_files = sorted(templates_dir.glob("*.md")) if templates_dir.exists() else []
    # A template directory by itself is not enough to activate this check. The
    # package must expose at least one external contract surface (gate,
    # binding, or registry) alongside its playbook state schema.
    applicable = source.exists() and bool(gate_files or binding_files or registry_path)
    if not applicable:
        return {"package": root.as_posix(), "status": "SKIPPED", "reason": "no applicable contract surfaces"}

    issues: list[dict[str, Any]] = []
    playbook = load_yaml(source)
    state = playbook.get("state", {}) if isinstance(playbook, dict) else {}
    schema = state.get("schema", {}) if isinstance(state, dict) else {}
    state_roots = set(schema) if isinstance(schema, dict) else set()

    registry = load_yaml(registry_path) if registry_path else {}
    registry_roots, _ = registry_paths(registry)
    all_binding_roots: set[str] = set()
    binding_sources: list[tuple[str, str, str, str]] = []
    for path in binding_files:
        roots, sources = binding_data(load_yaml(path))
        all_binding_roots |= roots
        binding_sources.extend((path.relative_to(root).as_posix(),) + item for item in sources)

    for artifact, key, state_root, source_ref in binding_sources:
        if state_root not in state_roots:
            issues.append({"id": "CAC-001", "severity": "error", "artifact": artifact,
                           "message": f"Binding {key!r} points to undeclared state root {state_root!r}: {source_ref}"})
    for state_root in sorted(registry_roots - state_roots):
        issues.append({"id": "CAC-002", "severity": "error", "artifact": args.registry,
                       "message": f"Variable registry references undeclared state root {state_root!r}"})
    for path in template_files:
        placeholders = {match.group(1).split(".")[0] for match in PLACEHOLDER.finditer(path.read_text(encoding="utf-8"))}
        for placeholder in sorted(placeholders - all_binding_roots):
            issues.append({"id": "CAC-003", "severity": "error", "artifact": path.relative_to(root).as_posix(),
                           "message": f"Template placeholder root {placeholder!r} has no binding"})

    live_parts = [yaml.safe_dump(schema, allow_unicode=True).lower()]
    if registry_path:
        live_parts.append(registry_path.read_text(encoding="utf-8").lower())
    for path in binding_files + template_files:
        live_parts.append(path.read_text(encoding="utf-8").lower())
    live_text = "\n".join(live_parts)

    gates: list[tuple[Path, dict[str, Any]]] = []
    for path in gate_files:
        gate = load_yaml(path)
        gates.append((path, gate if isinstance(gate, dict) else {}))
        checks = gate.get("checks", []) if isinstance(gate, dict) else []
        for check in checks or []:
            if not isinstance(check, dict):
                continue
            required = check.get("required_state_objects") or check.get("required_state_roots")
            tokens = {str(item).split(".", 1)[0] for item in required} if isinstance(required, list) else set()
            assertion = str(check.get("assertion", ""))
            match = PRESENT_PHRASE.search(assertion)
            if match:
                tokens |= {token for token in SNAKE.findall(match.group(1)) if token not in STOP_WORDS}
            for token in sorted(tokens):
                if token not in state_roots:
                    issues.append({"id": "CAC-004", "severity": "error", "artifact": path.relative_to(root).as_posix(),
                                   "check_id": check.get("id"),
                                   "message": f"Gate requires state object {token!r}, but it is not declared in state.schema"})

    domain_hits: dict[str, int] = {}
    locations: dict[str, list[tuple[str, Any]]] = {}
    for path, gate in gates:
        for check in gate.get("checks", []) or []:
            if not isinstance(check, dict):
                continue
            corpus = f"{check.get('name', '')} {check.get('assertion', '')}".lower()
            for word in re.findall(r"\b[a-z][a-z0-9]{4,}\b", corpus):
                if word in STOP_WORDS:
                    continue
                domain_hits[word] = domain_hits.get(word, 0) + 1
                locations.setdefault(word, []).append((path.relative_to(root).as_posix(), check.get("id")))
    for word, count in sorted(domain_hits.items()):
        if count >= 2 and re.search(rf"\b{re.escape(word)}\b", live_text) is None:
            issues.append({"id": "CAC-005", "severity": "error", "artifact": "gates/*",
                           "message": f"Gate semantic domain {word!r} is referenced {count} times but has no support in live contract surfaces",
                           "locations": locations[word]})

    status = "FAIL" if any(issue["severity"] == "error" for issue in issues) else "PASS"
    return {
        "package": root.as_posix(), "status": status,
        "summary": {"errors": sum(issue["severity"] == "error" for issue in issues),
                     "issues": len(issues), "state_roots": len(state_roots),
                     "binding_files": len(binding_files), "gate_files": len(gates)},
        "issues": issues,
    }


def discover_packages(repo_root: Path) -> list[Path]:
    packages: set[Path] = set()
    for base_name in ("packages", "integrations"):
        base = repo_root / base_name
        if not base.exists():
            continue
        for source in base.glob("**/source/program.ordo.y*ml"):
            packages.add(source.parent.parent)
    return sorted(packages)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--root", type=Path, help="one playbook package root")
    group.add_argument("--repo-root", type=Path, help="discover and check all repository playbook packages")
    parser.add_argument("--playbook", default="source/program.ordo.yaml")
    parser.add_argument("--gates-dir", default="gates")
    parser.add_argument("--templates-dir", default="output_templates")
    parser.add_argument("--registry", default="registry/VARIABLE_REGISTRY.yaml")
    parser.add_argument("--json-out", "--out", dest="json_out", type=Path)
    args = parser.parse_args(argv)

    if args.root:
        package_report = check_package(args.root, args)
        report = {"validator": "cross_artifact_contract_consistency", "version": "0.1.0",
                  "status": package_report["status"], "packages": [package_report],
                  "summary": {"checked": 1 if package_report["status"] != "SKIPPED" else 0,
                                                                    "skipped": 1 if package_report["status"] == "SKIPPED" else 0,
                                                                    "errors": len(package_report.get("issues", []))}}
    else:
        packages = discover_packages(args.repo_root.resolve())
        package_reports = [check_package(package, args) for package in packages]
        failures = [report for report in package_reports if report["status"] == "FAIL"]
        report = {"validator": "cross_artifact_contract_consistency", "version": "0.1.0",
                  "status": "FAIL" if failures else "PASS", "packages": package_reports,
                  "summary": {"checked": sum(report["status"] != "SKIPPED" for report in package_reports),
                              "skipped": sum(report["status"] == "SKIPPED" for report in package_reports),
                              "errors": sum(len(report.get("issues", [])) for report in failures)}}
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
