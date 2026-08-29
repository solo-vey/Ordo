from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import json
import os
from datetime import datetime, timezone

EXCLUDED_PARTS = {"__pycache__", ".git", ".ordo-generated"}
EXCLUDED_NAMES = {"package_report.json", "BUILD_MANIFEST.json", "SHA256SUMS.txt"}

def _included(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDED_PARTS for part in rel.parts):
        return False
    if path.suffix == ".pyc" or path.name in EXCLUDED_NAMES:
        return False
    if "reports" in rel.parts and path.name.startswith("ci_release_evidence"):
        return False
    return path.is_file()

def source_tree_sha256(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if _included(p, root)):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        h.update(len(rel).to_bytes(8, "big"))
        h.update(rel)
        data = path.read_bytes()
        h.update(len(data).to_bytes(8, "big"))
        h.update(data)
    return h.hexdigest()

def validate_ci_release_evidence(package_root: Path, evidence_path: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [{"severity": "error", "code": "ORDO-CI-001", "message": f"invalid CI release evidence: {exc}", "location": str(evidence_path)}]
    if evidence.get("schema_version") != "ordo.ci_release_evidence.v1":
        issues.append({"severity": "error", "code": "ORDO-CI-002", "message": "unsupported CI evidence schema", "location": str(evidence_path)})
    if evidence.get("status") != "passed":
        issues.append({"severity": "error", "code": "ORDO-CI-003", "message": "CI evidence is not green", "location": str(evidence_path)})
    matrix = evidence.get("test_matrix") or []
    if not matrix or any(item.get("status") != "passed" for item in matrix):
        issues.append({"severity": "error", "code": "ORDO-CI-004", "message": "required CI test matrix is incomplete or red", "location": str(evidence_path)})
    if evidence.get("source_tree_sha256") != source_tree_sha256(package_root):
        issues.append({"severity": "error", "code": "ORDO-CI-005", "message": "CI evidence does not match the current package tree", "location": str(evidence_path)})
    expected_revision = os.environ.get("GITHUB_SHA")
    if expected_revision and evidence.get("revision") != expected_revision:
        issues.append({"severity": "error", "code": "ORDO-CI-006", "message": "CI evidence revision does not match GITHUB_SHA", "location": str(evidence_path)})
    if not evidence.get("run_id"):
        issues.append({"severity": "error", "code": "ORDO-CI-007", "message": "CI evidence has no run_id", "location": str(evidence_path)})

    issued_at = evidence.get("issued_at")
    if not issued_at:
        issues.append({"severity": "error", "code": "ORDO-CI-009", "message": "CI evidence has no issued_at timestamp", "location": str(evidence_path)})
    else:
        try:
            issued = datetime.fromisoformat(issued_at.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            max_age_seconds = int(os.environ.get("ORDO_CI_EVIDENCE_MAX_AGE_SECONDS", "86400"))
            age = (now - issued.astimezone(timezone.utc)).total_seconds()
            if age < 0 or age > max_age_seconds:
                issues.append({"severity": "error", "code": "ORDO-CI-010", "message": "CI evidence is stale or timestamp is invalid", "location": str(evidence_path)})
        except Exception:
            issues.append({"severity": "error", "code": "ORDO-CI-011", "message": "CI evidence issued_at timestamp is invalid", "location": str(evidence_path)})
    return issues
