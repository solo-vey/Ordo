from __future__ import annotations

from typing import Any
import hashlib
import json
import re

ORDO_TOKENS = [
    r"\bordo\b",
    r"\bexecution mode\b",
    r"\bstate\.snapshot\b",
    r"\bdecision\.log\b",
    r"\bgate\.report\b",
    r"\bpath\.explain\b",
    r"\bprogram-level contract\b",
    r"\bprocess rail\b",
]

def canonical_shared_payload(task: dict[str, Any]) -> bytes:
    payload = {
        "shared_input": task["shared_input"],
        "acceptance_criteria": task["acceptance_criteria"],
        "required_output": task["required_output"],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def shared_payload_sha256(task: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_shared_payload(task)).hexdigest()

def scan_plain_prompt(
    prompt: str,
    allowed_shared_texts: list[str] | None = None,
) -> list[dict[str, str]]:
    scan_target = prompt
    for shared in allowed_shared_texts or []:
        if shared:
            scan_target = scan_target.replace(shared, "")
    issues = []
    for pattern in ORDO_TOKENS:
        if re.search(pattern, scan_target, flags=re.IGNORECASE):
            issues.append({
                "code": "ORDO-AB-CONTAM-001",
                "pattern": pattern,
                "message": "Ordo-specific content leaked into Plain Prompt arm outside frozen shared task content",
            })
    return issues

def validate_arm_equivalence(
    task: dict[str, Any],
    arm_a_payload: dict[str, Any],
    arm_b_payload: dict[str, Any],
) -> list[dict[str, str]]:
    issues = []
    frozen = ["shared_input", "acceptance_criteria", "required_output"]
    for field in frozen:
        expected = task.get(field)
        if arm_a_payload.get(field) != expected:
            issues.append({
                "code": "ORDO-AB-CONTAM-002",
                "field": field,
                "message": "Arm A differs from frozen shared task content",
            })
        if arm_b_payload.get(field) != expected:
            issues.append({
                "code": "ORDO-AB-CONTAM-003",
                "field": field,
                "message": "Arm B differs from frozen shared task content",
            })
    return issues

def build_arm_payloads(task: dict[str, Any], plain_prompt: str, ordo_prompt: str) -> dict[str, Any]:
    shared = {
        "shared_input": task["shared_input"],
        "acceptance_criteria": task["acceptance_criteria"],
        "required_output": task["required_output"],
    }
    return {
        "shared_payload_sha256": shared_payload_sha256(task),
        "A": {**shared, "prompt": plain_prompt},
        "B": {**shared, "prompt": ordo_prompt},
    }
