"""Fail-closed package checks for canonical validator propagation."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any


CONTRACT_NAME = "validator_propagation_contract.json"


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def validate_validator_propagation(package: str | Path, *, repo_root: str | Path) -> dict[str, Any]:
    """Ensure declared shipped validator files equal their canonical sources.

    A package opts in by carrying ``validator_propagation_contract.json`` at its
    root.  Each mapping is repository-relative on the canonical side and
    package-relative on the delivery side.  Missing mappings or byte drift are
    blocking: a local validator change cannot silently evade a release package.
    """
    root = Path(package).resolve()
    canonical_root = Path(repo_root).resolve()
    path = root / CONTRACT_NAME
    if not path.is_file():
        return {"schema_version": "ordo.validator_propagation.v1", "status": "not_enabled", "package": str(root), "issues": [], "checked_mappings": []}
    issues: list[dict[str, Any]] = []
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"schema_version": "ordo.validator_propagation.v1", "status": "failed", "package": str(root), "issues": [{"severity": "error", "code": "VALIDATOR_PROPAGATION_CONTRACT_INVALID", "message": str(exc), "location": CONTRACT_NAME}], "checked_mappings": []}
    mappings = contract.get("mappings") if isinstance(contract, dict) else None
    if contract.get("schema_version") != "1.0" or not isinstance(mappings, list) or not mappings:
        return {"schema_version": "ordo.validator_propagation.v1", "status": "failed", "package": str(root), "issues": [{"severity": "error", "code": "VALIDATOR_PROPAGATION_CONTRACT_INVALID", "message": "contract requires schema_version 1.0 and a non-empty mappings list.", "location": CONTRACT_NAME}], "checked_mappings": []}
    checked: list[dict[str, str]] = []
    for index, mapping in enumerate(mappings):
        if not isinstance(mapping, dict) or not isinstance(mapping.get("canonical"), str) or not isinstance(mapping.get("packaged"), str):
            issues.append({"severity": "error", "code": "VALIDATOR_PROPAGATION_MAPPING_INVALID", "message": "mapping needs canonical and packaged relative paths.", "location": f"mappings[{index}]"})
            continue
        canonical = canonical_root / mapping["canonical"]
        packaged = root / mapping["packaged"]
        if not canonical.is_file() or not packaged.is_file():
            issues.append({"severity": "error", "code": "VALIDATOR_PROPAGATION_FILE_MISSING", "message": "canonical or packaged validator file is missing.", "location": f"mappings[{index}]"})
            continue
        source_hash, package_hash = _digest(canonical), _digest(packaged)
        checked.append({"canonical": mapping["canonical"], "packaged": mapping["packaged"], "sha256": package_hash})
        if source_hash != package_hash:
            issues.append({"severity": "error", "code": "VALIDATOR_PROPAGATION_HASH_MISMATCH", "message": "packaged validator differs from canonical source.", "location": mapping["packaged"], "canonical": mapping["canonical"]})
    return {
        "schema_version": "ordo.validator_propagation.v1",
        "status": "passed" if not issues else "failed",
        "package": str(root),
        "contract": CONTRACT_NAME,
        "checked_mappings": checked,
        "issues": issues,
    }
