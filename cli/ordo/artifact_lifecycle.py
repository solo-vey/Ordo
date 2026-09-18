from __future__ import annotations

"""Physical-output-bound artifact review, approval, and delivery lifecycle."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from .loader import load_package
from .reporter import write_json


SCHEMA = "ordo.artifact_lifecycle_report.v1"
STATES = ("generated", "reviewed", "approved", "delivered")
_NEXT = {"generated": "reviewed", "reviewed": "approved", "approved": "delivered"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _issue(code: str, message: str, location: str) -> dict[str, str]:
    return {"severity": "error", "code": code, "message": message, "location": location}


def _safe_artifact(root: Path, raw: Any) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    path = (root / raw).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None
    return path


def _load_manifest(root: Path, issues: list[dict[str, str]]) -> tuple[Path, dict[str, Any]]:
    path = root / "generated_outputs" / "output_manifest.json"
    if not path.is_file():
        issues.append(_issue("ARTIFACT_LIFECYCLE_MANIFEST_MISSING", "generated output manifest is missing", "generated_outputs/output_manifest.json"))
        return path, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        issues.append(_issue("ARTIFACT_LIFECYCLE_MANIFEST_INVALID", f"cannot parse output manifest: {exc}", "generated_outputs/output_manifest.json"))
        return path, {}
    if not isinstance(data, dict):
        issues.append(_issue("ARTIFACT_LIFECYCLE_MANIFEST_INVALID", "output manifest must be a JSON object", "generated_outputs/output_manifest.json"))
        return path, {}
    return path, data


def _lifecycle(artifact: dict[str, Any]) -> dict[str, Any]:
    value = artifact.get("lifecycle")
    return value if isinstance(value, dict) else {}


def _validate_artifact(root: Path, artifact: dict[str, Any], index: int) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    label = f"artifacts[{index}]"
    artifact_id = artifact.get("id")
    if not isinstance(artifact_id, str) or not artifact_id:
        issues.append(_issue("ARTIFACT_LIFECYCLE_ID_MISSING", "artifact id is required", label + ".id"))
    raw_path = artifact.get("path")
    physical = _safe_artifact(root, raw_path)
    if physical is None or not physical.is_file():
        issues.append(_issue("ARTIFACT_PHYSICAL_FILE_MISSING", "artifact must reference an existing file inside the package", label + ".path"))
        return issues
    actual_hash = sha256_file(physical)
    if artifact.get("hash") != actual_hash:
        issues.append(_issue("ARTIFACT_PHYSICAL_HASH_MISMATCH", "artifact hash does not match its physical file", label + ".hash"))
    lifecycle = _lifecycle(artifact)
    state = lifecycle.get("state")
    if state not in STATES:
        issues.append(_issue("ARTIFACT_LIFECYCLE_STATE_INVALID", "lifecycle state must be generated, reviewed, approved, or delivered", label + ".lifecycle.state"))
        return issues
    generated = lifecycle.get("generated") if isinstance(lifecycle.get("generated"), dict) else {}
    if generated.get("status") != "generated" or generated.get("sha256") != actual_hash:
        issues.append(_issue("ARTIFACT_GENERATION_EVIDENCE_INVALID", "generated evidence must bind the current physical file hash", label + ".lifecycle.generated"))
    delivery = lifecycle.get("delivery") if isinstance(lifecycle.get("delivery"), dict) else {}
    download = delivery.get("download") if isinstance(delivery.get("download"), dict) else {}
    href = download.get("href")
    download_file = _safe_artifact(root, href)
    if download_file is None or not download_file.is_file() or download_file.resolve() != physical.resolve():
        issues.append(_issue("ARTIFACT_DOWNLOAD_LINK_INVALID", "download href must be a package-relative link to the exact physical artifact", label + ".lifecycle.delivery.download.href"))
    if state in {"reviewed", "approved", "delivered"}:
        reviewed = lifecycle.get("reviewed") if isinstance(lifecycle.get("reviewed"), dict) else {}
        if reviewed.get("status") != "reviewed" or not isinstance(reviewed.get("reviewed_by"), str) or not reviewed.get("reviewed_by"):
            issues.append(_issue("ARTIFACT_REVIEW_EVIDENCE_MISSING", "reviewed, approved, and delivered artifacts require reviewer evidence", label + ".lifecycle.reviewed"))
    if state in {"approved", "delivered"}:
        approved = lifecycle.get("approved") if isinstance(lifecycle.get("approved"), dict) else {}
        if approved.get("status") != "approved" or not isinstance(approved.get("approved_by"), str) or not approved.get("approved_by"):
            issues.append(_issue("ARTIFACT_APPROVAL_EVIDENCE_MISSING", "approved and delivered artifacts require approval evidence", label + ".lifecycle.approved"))
    if state == "delivered" and delivery.get("status") != "delivered":
        issues.append(_issue("ARTIFACT_DELIVERY_EVIDENCE_MISSING", "delivered artifact requires delivery evidence", label + ".lifecycle.delivery"))
    return issues


def validate_artifact_lifecycle(package_path: str | Path) -> dict[str, Any]:
    root, _manifest, _source, _tests = load_package(package_path)
    issues: list[dict[str, str]] = []
    manifest_path, manifest = _load_manifest(root, issues)
    artifacts = manifest.get("artifacts") if isinstance(manifest.get("artifacts"), list) else []
    if not issues and not artifacts:
        issues.append(_issue("ARTIFACT_LIFECYCLE_ARTIFACTS_MISSING", "output manifest must contain artifacts", "generated_outputs/output_manifest.json"))
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            issues.append(_issue("ARTIFACT_LIFECYCLE_RECORD_INVALID", "artifact record must be an object", f"artifacts[{index}]"))
            continue
        issues.extend(_validate_artifact(root, artifact, index))
    states = {state: 0 for state in STATES}
    for artifact in artifacts:
        if isinstance(artifact, dict) and _lifecycle(artifact).get("state") in states:
            states[_lifecycle(artifact)["state"]] += 1
    return {
        "schema_version": SCHEMA,
        "status": "passed" if not issues else "blocked",
        "manifest": str(manifest_path.relative_to(root)),
        "summary": {"artifacts": len(artifacts), "states": states, "errors": len(issues)},
        "issues": issues,
    }


def advance_artifact_lifecycle(
    package_path: str | Path,
    *,
    artifact_id: str,
    target_state: str,
    actor: str,
    out: str | Path | None = None,
) -> dict[str, Any]:
    """Advance exactly one state after validating the physical artifact first."""
    root, _manifest, _source, _tests = load_package(package_path)
    issues: list[dict[str, str]] = []
    manifest_path, manifest = _load_manifest(root, issues)
    artifacts = manifest.get("artifacts") if isinstance(manifest.get("artifacts"), list) else []
    matches = [item for item in artifacts if isinstance(item, dict) and item.get("id") == artifact_id]
    if len(matches) != 1:
        issues.append(_issue("ARTIFACT_LIFECYCLE_ARTIFACT_UNKNOWN", "artifact id must identify exactly one manifest artifact", "--artifact"))
        artifact: dict[str, Any] = {}
    else:
        artifact = matches[0]
        issues.extend(_validate_artifact(root, artifact, artifacts.index(artifact)))
    current = _lifecycle(artifact).get("state")
    if target_state not in STATES:
        issues.append(_issue("ARTIFACT_LIFECYCLE_TARGET_INVALID", "target state must be reviewed, approved, or delivered", "--to"))
    elif current and _NEXT.get(current) != target_state:
        issues.append(_issue("ARTIFACT_LIFECYCLE_PREMATURE_TRANSITION", f"cannot transition directly from {current} to {target_state}", "--to"))
    if not isinstance(actor, str) or not actor.strip():
        issues.append(_issue("ARTIFACT_LIFECYCLE_ACTOR_MISSING", "a non-empty actor is required", "--actor"))
    if issues:
        report = {"schema_version": "ordo.artifact_lifecycle_transition_report.v1", "status": "blocked", "artifact_id": artifact_id, "from": current, "to": target_state, "issues": issues}
    else:
        lifecycle = artifact["lifecycle"]
        if target_state == "reviewed":
            lifecycle["reviewed"] = {"status": "reviewed", "reviewed_by": actor, "reviewed_at": utc_now()}
        elif target_state == "approved":
            lifecycle["approved"] = {"status": "approved", "approved_by": actor, "approved_at": utc_now()}
        elif target_state == "delivered":
            lifecycle["delivery"]["status"] = "delivered"
            lifecycle["delivery"]["delivered_by"] = actor
            lifecycle["delivery"]["delivered_at"] = utc_now()
        lifecycle["state"] = target_state
        write_json(manifest_path, manifest)
        report = {"schema_version": "ordo.artifact_lifecycle_transition_report.v1", "status": "advanced", "artifact_id": artifact_id, "from": current, "to": target_state, "manifest": str(manifest_path.relative_to(root)), "issues": []}
    target = Path(out).resolve() if out else root / "reports" / "artifact_lifecycle_transition_report.json"
    write_json(target, report)
    report["output"] = str(target)
    return report
