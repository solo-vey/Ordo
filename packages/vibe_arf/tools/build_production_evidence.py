#!/usr/bin/env python3
"""Materialize reproducible production evidence in a disposable Vibe staging tree."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    root = args.package.resolve()
    if not (root / "source" / "program.ordo.yaml").is_file():
        raise SystemExit("source/program.ordo.yaml is required")
    source = root / "source" / "program.ordo.yaml"
    tools = root / "tools"
    for script in ("publish_authoring_data_flow.py", "materialize_production_dependency_closure.py"):
        result = subprocess.run([sys.executable, str(tools / script), str(root)], text=True, capture_output=True)
        if result.returncode:
            raise SystemExit(f"{script} failed:\n{result.stdout}\n{result.stderr}")
    design = root / "design"
    evidence = {
        "schema_version": "1.0",
        "kind": "vibe_arf_production_evidence",
        "source": {"path": "source/program.ordo.yaml", "sha256": digest(source)},
        "scope": "staging_only",
    }
    (design / "PRODUCTION_EVIDENCE.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    impact = {
        "schema_version": "1.0", "generated_in_staging": True, "source_sha256": evidence["source"]["sha256"],
        "ignore_globs": ["reports/**", "design/**", "generated_outputs/**", "*.pyc", "__pycache__/**"],
        "modes": {
            "PATCH": {"validation_class": "FAST", "full_pre_editor": False, "budget_seconds": 8, "safety_checks": []},
            "CHECKPOINT": {"validation_class": "FAST", "full_pre_editor": False, "budget_seconds": 20, "safety_checks": []},
            "CANDIDATE": {"validation_class": "TARGETED", "full_pre_editor": False, "budget_seconds": 120, "shard_size": 8, "safety_checks": []},
            "RELEASE": {"validation_class": "FULL", "full_pre_editor": True, "budget_seconds": 600, "safety_checks": []}
        },
        "path_rules": [
            {"globs": ["README.md", "START_HERE*.md", "START_PROMPT*.md"], "checks": ["entry_docs_revision"], "exclusive": True},
            {"globs": ["source/data-layer-first-hard-architecture-policy.json"], "checks": ["data_layer_first_hard_architecture"], "exclusive": True},
            {"globs": ["source/reusable-authoring-template-policy.json"], "checks": ["reusable_authoring_templates"], "exclusive": True},
            {"globs": ["source/quality_acceptance_policy.json"], "checks": ["hybrid_reference_fidelity_feedback"], "exclusive": True},
            {"globs": ["source/deterministic-first-execution-policy.json"], "checks": ["deterministic_first_execution"], "exclusive": True},
            {"globs": ["source/information-preservation-policy.json"], "checks": ["information_preservation_monotonic_evidence"], "exclusive": True},
            {"globs": ["source/editor-visible-architecture-policy.json"], "checks": ["editor_visible_architecture"], "exclusive": True},
            {"globs": ["source/default-debug-handoff-progress-policy.json"], "checks": ["default_debug_handoff_progress"], "exclusive": True}
        ]
    }
    (root / "verification_impact_map.json").write_text(json.dumps(impact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "generated": ["design/", "PRODUCTION_DEPENDENCY_CLOSURE.json", "verification_impact_map.json"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
