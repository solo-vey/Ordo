"""Layer-specific validation reporting for executable Ordo packages.

The ordinary linter remains a convenient aggregate gate.  This module exposes
the same concerns as independent evidence layers so that a consumer can tell
whether a failure belongs to source shape, graph structure, state lineage,
artifact mapping, or higher-level interaction semantics.
"""
from __future__ import annotations

from typing import Any, Callable

from .analyst_interaction import validate_analyst_interaction_contract
from .contract_coverage import validate_contract_artifact_coverage
from .correction_replay import validate_correction_contract
from .flow_reuse_validation import validate_flow_reuse
from .graph_validation import validate_process_graph
from .input_contract import validate_input_contract
from .state_lineage import validate_state_lineage
from .value_provenance import validate_value_provenance_contract


PASSING_STATUSES = {"passed", "not_enabled", "not_applicable"}


def _issues(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in (report.get("issues") or []) if isinstance(item, dict)]


def _basic_schema(source: dict[str, Any]) -> dict[str, Any]:
    """Validate the minimal parsed source shape before deeper layers run."""
    issues: list[dict[str, Any]] = []
    if not isinstance(source.get("ordo"), dict):
        issues.append({"severity": "error", "code": "LAYER_SCHEMA_ORDO_REQUIRED", "message": "source must contain an ordo mapping.", "location": "ordo"})
    for key in ("nodes", "gates", "terminals"):
        if key in source and not isinstance(source[key], list):
            issues.append({"severity": "error", "code": "LAYER_SCHEMA_COLLECTION_INVALID", "message": f"{key} must be a list when declared.", "location": key})
    identifiers: list[str] = []
    for key in ("nodes", "gates", "terminals"):
        for index, item in enumerate(source.get(key) or []):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
                issues.append({"severity": "error", "code": "LAYER_SCHEMA_ID_REQUIRED", "message": "every declared graph element needs an id.", "location": f"{key}[{index}].id"})
            else:
                identifiers.append(item["id"])
    duplicate_ids = sorted({item for item in identifiers if identifiers.count(item) > 1})
    for item in duplicate_ids:
        issues.append({"severity": "error", "code": "LAYER_SCHEMA_DUPLICATE_ID", "message": f"duplicate graph identifier: {item}", "location": "nodes/gates/terminals"})
    return {
        "status": "passed" if not issues else "failed",
        "summary": {"errors": len(issues), "elements": len(identifiers)},
        "issues": issues,
    }


def _combine(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    issues = [issue for report in reports.values() for issue in _issues(report)]
    failed = [name for name, report in reports.items() if str(report.get("status", "failed")) not in PASSING_STATUSES]
    return {
        "status": "passed" if not failed else "failed",
        "summary": {"validators": len(reports), "failed": len(failed), "errors": len([issue for issue in issues if issue.get("severity", "error") == "error"])},
        "validators": reports,
        "issues": issues,
    }


def validate_layers(source: dict[str, Any], tests: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return separately attributable validation evidence for one source tree."""
    tests = tests if isinstance(tests, dict) else {}
    semantic = _combine({
        "input_contract": validate_input_contract(source),
        "value_provenance": validate_value_provenance_contract(source),
        "analyst_interaction": validate_analyst_interaction_contract(source),
        "correction_replay": validate_correction_contract(source, tests),
        "flow_reuse": validate_flow_reuse(source),
    })
    layers = {
        "schema": _basic_schema(source),
        "graph": validate_process_graph(source),
        "lineage": validate_state_lineage(source),
        "artifact": validate_contract_artifact_coverage(source),
        "semantic": semantic,
    }
    failed = [name for name, report in layers.items() if str(report.get("status", "failed")) not in PASSING_STATUSES]
    return {
        "schema_version": "ordo.validation_layers.v1",
        "status": "passed" if not failed else "failed",
        "layer_order": ["schema", "graph", "lineage", "artifact", "semantic"],
        "summary": {"layers": len(layers), "failed_layers": failed},
        "layers": layers,
    }
