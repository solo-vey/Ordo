from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any
import hashlib
import json
import yaml

from .prompt_registry_reconcile import reconcile_prompt_registry


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _audit_external_registry(integration_root: Path) -> dict[str, Any]:
    registry_path = integration_root / "docs" / "APF_PROMPT_REGISTRY.yaml"
    manifest_path = integration_root / "prompts" / "PROMPT_MANIFEST.json"
    errors: list[str] = []
    if not registry_path.is_file() or not manifest_path.is_file():
        return {"status": "failed", "errors": ["registry_or_manifest_missing"]}
    registry_doc = yaml.safe_load(registry_path.read_text()) or {}
    registry = registry_doc.get("prompt_registry", {}) or {}
    entries = registry.get("prompts", []) or []
    manifest = json.loads(manifest_path.read_text())
    m_entries = manifest.get("prompts", []) or []
    ids = [str(x.get("prompt_id")) for x in entries]
    mids = [str(x.get("prompt_id")) for x in m_entries]
    duplicate_ids = sorted(k for k, v in Counter(ids).items() if v > 1)
    if duplicate_ids:
        errors.append("duplicate_prompt_ids")
    if set(ids) != set(mids):
        errors.append("registry_manifest_id_mismatch")
    by_manifest = {str(x.get("prompt_id")): x for x in m_entries}
    checksum_mismatches: list[str] = []
    authority_violations: list[str] = []
    for entry in entries:
        pid = str(entry.get("prompt_id"))
        path = integration_root / str(entry.get("path", ""))
        m = by_manifest.get(pid, {})
        if not path.is_file():
            checksum_mismatches.append(pid)
            continue
        size = m.get("size_bytes", m.get("bytes"))
        if m.get("sha256") != _sha(path) or size != path.stat().st_size:
            checksum_mismatches.append(pid)
        if entry.get("state_change_allowed") is not False:
            authority_violations.append(pid)
        if entry.get("lifecycle") not in {"stable", "deprecated", "experimental"}:
            authority_violations.append(pid)
    if checksum_mismatches:
        errors.append("checksum_mismatch")
    if authority_violations:
        errors.append("authority_boundary_violation")
    return {
        "status": "passed" if not errors else "failed",
        "registry_entries": len(entries),
        "manifest_entries": len(m_entries),
        "duplicate_prompt_ids": duplicate_ids,
        "checksum_mismatches": sorted(checksum_mismatches),
        "authority_violations": sorted(set(authority_violations)),
        "errors": errors,
    }


def _audit_candidates(integration_root: Path) -> dict[str, Any]:
    base = integration_root / "improvements" / "playbook_authored_mini_prompts"
    candidates = sorted(base.glob("pilots/*/candidates/*.yaml"))
    reviews = sorted(base.glob("pilots/*/reviews/*.yaml"))
    review_by_id = {}
    for path in reviews:
        rec = (yaml.safe_load(path.read_text()) or {}).get("review_record", {}) or {}
        review_by_id[str(rec.get("candidate_id"))] = rec
    errors: list[dict[str, str]] = []
    rows = []
    required_prohibitions = {
        "no_navigation_authority", "no_gate_bypass", "no_human_confirmation_authority",
        "no_confirmed_state_mutation", "no_hidden_business_logic", "no_package_scope_expansion",
    }
    for path in candidates:
        c = (yaml.safe_load(path.read_text()) or {}).get("candidate", {}) or {}
        cid = str(c.get("candidate_id"))
        review = review_by_id.get(cid)
        if review is None:
            errors.append({"candidate_id": cid, "issue": "review_missing"})
        prohibited = set(c.get("prohibited_authority", []) or [])
        if not required_prohibitions.issubset(prohibited):
            errors.append({"candidate_id": cid, "issue": "authority_boundary_incomplete"})
        status = str(c.get("candidate_status"))
        approved = bool(review and review.get("status") == "approved" and review.get("activation_allowed") is True)
        if status != "approved" and approved:
            errors.append({"candidate_id": cid, "issue": "activation_without_candidate_approval"})
        if status in {"proposed", "needs_revision", "deferred"} and review and review.get("activation_allowed") is True:
            errors.append({"candidate_id": cid, "issue": "preapproval_activation"})
        rows.append({"candidate_id": cid, "candidate_status": status, "review_status": None if review is None else review.get("status"), "activation_allowed": False if review is None else bool(review.get("activation_allowed"))})
    return {"status": "passed" if not errors else "failed", "candidate_count": len(candidates), "review_count": len(reviews), "candidates": rows, "errors": errors}


def audit_prompt_governance(repository_root: str | Path) -> dict[str, Any]:
    root = Path(repository_root)
    package_results = []
    errors = []
    for pkg in sorted((root / "packages").iterdir()):
        source = pkg / "source" / "program.ordo.yaml"
        if not source.is_file():
            continue
        doc = yaml.safe_load(source.read_text()) or {}
        has_registry = bool((doc.get("prompt_registry") or {}).get("prompts"))
        has_refs = "prompt_refs" in source.read_text()
        if has_registry:
            result = reconcile_prompt_registry(pkg)
            package_results.append({"package": pkg.name, "registry_mode": "active", "status": result["status"], "details": result})
            if result["status"] != "passed":
                errors.append(f"package:{pkg.name}")
        else:
            status = "failed" if has_refs else "passed"
            package_results.append({"package": pkg.name, "registry_mode": "not_declared", "status": status, "details": {"prompt_refs_without_registry": has_refs}})
            if status != "passed":
                errors.append(f"package_prompt_refs_without_registry:{pkg.name}")
    integration_root = root / "integrations" / "apf" / "v0.1.0-rc.18"
    apf_registry = _audit_external_registry(integration_root)
    candidate_governance = _audit_candidates(integration_root)
    review_path = root / "reports" / "m78_1_apf_internal_mini_prompt_review" / "M78_1_APF_INTERNAL_MINI_PROMPT_APPLICABILITY_REVIEW.json"
    review = json.loads(review_path.read_text()) if review_path.is_file() else {}
    review_ok = (
        review.get("summary", {}).get("internal_prompts_to_activate") == 0
        and review.get("summary", {}).get("decision") == "internal_mini_prompts_not_applicable_in_current_baseline"
        and len(review.get("reopen_conditions", [])) >= 4
    )
    if apf_registry["status"] != "passed": errors.append("apf_registry")
    if candidate_governance["status"] != "passed": errors.append("candidate_governance")
    if not review_ok: errors.append("internal_mini_prompt_review")
    return {
        "schema_version": "ordo.prompt_governance_audit.v1",
        "status": "passed" if not errors else "failed",
        "package_results": package_results,
        "apf_registry": apf_registry,
        "candidate_governance": candidate_governance,
        "internal_mini_prompt_review": {"status": "passed" if review_ok else "failed", "decision": review.get("summary", {}).get("decision")},
        "blocking_issues": errors,
    }
