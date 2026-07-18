from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import copy
import json
import re

from .loader import load_package, load_yaml
from .reporter import write_json
from .csg_runtime import apply_csg_events


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initial_state(source: dict[str, Any]) -> dict[str, Any]:
    schema = ((source.get("state") or {}).get("schema") or {})
    return copy.deepcopy(schema)


def get_path(data: dict[str, Any], path: str) -> Any:
    cur: Any = data
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def set_path(data: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    cur = data
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


def resolve_answer_placeholder(answer: Any, expression: Any) -> Any:
    if expression == "$answer":
        return answer
    if isinstance(expression, str) and expression.startswith("$answer."):
        path = expression[len("$answer."):]
        cur = answer
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur
    return expression


def state_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    keys = sorted(set(before.keys()) | set(after.keys()))
    diff: dict[str, Any] = {}
    for key in keys:
        if before.get(key) != after.get(key):
            diff[key] = {"before": before.get(key), "after": after.get(key)}
    return diff


def _is_truthy(value: Any) -> bool:
    return value not in (None, False, "", [], {})


def evaluate_mechanical_condition(condition: str, state: dict[str, Any]) -> tuple[str, str]:
    """Return (status, reason) for a small safe subset of mechanical conditions.

    This MVP intentionally supports only explicit patterns. Unknown mechanical
    conditions are blocked instead of guessed by the model.
    """
    normalized = " ".join((condition or "").strip().split())
    # Support a small conjunction subset first. This is intentionally
    # deterministic and conservative: unknown fragments block instead of being
    # guessed by the AI.
    if " and " in normalized:
        parts = normalized.split(" and ")
        results = [evaluate_mechanical_condition(part, state) for part in parts]
        if all(status == "passed" for status, _ in results):
            return ("passed", "all mechanical subconditions passed: " + "; ".join(reason for _, reason in results))
        return ("blocked", "one or more mechanical subconditions blocked: " + "; ".join(reason for _, reason in results))
    if " or " in normalized:
        parts = normalized.split(" or ")
        results = [evaluate_mechanical_condition(part, state) for part in parts]
        if any(status == "passed" for status, _ in results):
            return ("passed", "one or more mechanical subconditions passed: " + "; ".join(reason for _, reason in results))
        return ("blocked", "all mechanical subconditions blocked: " + "; ".join(reason for _, reason in results))

    one_of = re.match(r"^state\.([A-Za-z0-9_\.]+) is one of (.+)$", normalized)
    if one_of:
        field = one_of.group(1)
        allowed = [item.strip() for item in one_of.group(2).split(",")]
        value = get_path(state, field)
        return ("passed" if str(value) in allowed else "blocked", f"mechanical condition evaluated: {condition}; state.{field}={value!r}; allowed={allowed!r}")

    patterns = [
        (r"^state\.([A-Za-z0-9_\.]+) is not null$", lambda v: v is not None),
        (r"^state\.([A-Za-z0-9_\.]+) != null$", lambda v: v is not None),
        (r"^state\.([A-Za-z0-9_\.]+) is null$", lambda v: v is None),
        (r"^state\.([A-Za-z0-9_\.]+) == null$", lambda v: v is None),
        (r"^state\.([A-Za-z0-9_\.]+) is true$", lambda v: v is True),
        (r"^state\.([A-Za-z0-9_\.]+) == true$", lambda v: v is True),
        (r"^state\.([A-Za-z0-9_\.]+) is false$", lambda v: v is False),
        (r"^state\.([A-Za-z0-9_\.]+) == false$", lambda v: v is False),
        (r"^state\.([A-Za-z0-9_\.]+) is not empty$", lambda v: _is_truthy(v)),
        (r"^state\.([A-Za-z0-9_\.]+) is empty$", lambda v: not _is_truthy(v)),
    ]
    for pattern, predicate in patterns:
        m = re.match(pattern, normalized)
        if m:
            field = m.group(1)
            value = get_path(state, field)
            passed = predicate(value)
            return ("passed" if passed else "blocked", f"mechanical condition evaluated: {condition}; state.{field}={value!r}")
    return ("blocked", f"unsupported mechanical condition syntax: {condition!r}")


def apply_answers(source: dict[str, Any], state: dict[str, Any], answers: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    nodes = {n.get("id"): n for n in source.get("nodes", []) or []}
    for node_id, answer in (answers or {}).items():
        node = nodes.get(node_id)
        if not node:
            events.append({"type": "answer_ignored", "node": node_id, "reason": "node not found"})
            continue
        before = copy.deepcopy(state)
        on_answer = node.get("on_answer") or {}
        update: dict[str, Any] = {}
        next_target = None
        if isinstance(on_answer, dict) and "update_state" in on_answer:
            update = on_answer.get("update_state") or {}
            next_target = on_answer.get("next")
        elif isinstance(on_answer, dict) and isinstance(answer, str) and any(str(k).lower() == answer.lower() for k in on_answer.keys()):
            matched_key = next(k for k in on_answer.keys() if str(k).lower() == answer.lower())
            branch = on_answer.get(matched_key) or {}
            update = branch.get("update_state") or {}
            next_target = branch.get("next")
        elif isinstance(on_answer, dict) and node.get("allowed_answers") and answer not in node.get("allowed_answers", []):
            events.append({
                "type": "clarify_requested",
                "node": node_id,
                "answer": answer,
                "on_unmatched_input": node.get("on_unmatched_input"),
            })
            continue
        for key, value in update.items():
            set_path(state, key, resolve_answer_placeholder(answer, value))
        events.append({
            "type": "state_update",
            "node": node_id,
            "answer": answer,
            "next": next_target,
            "state_diff": state_diff(before, state),
        })
    return events


def evaluate_gates(source: dict[str, Any], state: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for gate in source.get("gates", []) or []:
        method = gate.get("method")
        if method == "mechanical":
            status, reason = evaluate_mechanical_condition(gate.get("condition", ""), state)
        elif method == "human":
            # MVP cannot perform human decision; it reports pending unless condition can be inferred from state.
            status = "pending_human"
            reason = "human gate requires explicit external confirmation; M3 runner does not decide it"
            condition = gate.get("condition", "") or ""
            if "approval_received" in condition and state.get("approval_received") is True:
                status = "passed"
                reason = "approval_received=True in state; treated as explicit user-confirmed state for MVP run"
        elif method in {"self_verification", "self_consistency"}:
            status = "pending_model"
            reason = f"{method} gate requires model verification; M3 runner records pending status"
        else:
            status = "blocked"
            reason = f"unknown gate.method: {method!r}"
        results.append({
            "id": gate.get("id"),
            "method": method,
            "trust_class": gate.get("trust_class"),
            "status": status,
            "condition": gate.get("condition"),
            "reason": reason,
        })
    return results


def _parse_literal(raw: str) -> Any:
    value = raw.strip()
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "null":
        return None
    return value


def _get_source_or_state_path(source: dict[str, Any], state: dict[str, Any], path: str) -> tuple[bool, Any, str]:
    source_value = get_path(source, path)
    if source_value is not None:
        return True, source_value, "source"
    state_value = get_path(state, path)
    if state_value is not None or path in state:
        return True, state_value, "state"
    return False, None, "missing"


def evaluate_assertion_condition(condition: str, source: dict[str, Any], state: dict[str, Any], gate_status: dict[str, str]) -> tuple[bool, bool, str]:
    """Return (evaluated, condition_truth, reason) for assertion conditions.

    Evaluated conditions are behaviorally checked by deterministic state/source logic.
    Unknown high-level semantic conditions remain structural-only instead of being guessed.
    """
    normalized = " ".join((condition or "").strip().split())
    if not normalized:
        return False, False, "empty condition; structural-only assertion"

    if normalized == "final_package_created_without_approval":
        final_created = state.get("final_package_created") is True
        approval = state.get("approval_received") is True or gate_status.get("G_APPROVAL_CONFIRMED") == "passed"
        return True, final_created and not approval, "checked final_package_created without approval_received/G_APPROVAL_CONFIRMED"

    if normalized == "semantic_ir_compiled_without_approval":
        compiled = state.get("semantic_ir_compiled") is True
        approval = state.get("approval_before_compile") is True or state.get("approval_received") is True or gate_status.get("G_APPROVAL_CONFIRMED") == "passed"
        return True, compiled and not approval, "checked semantic_ir_compiled without approval_before_compile/approval_received/G_APPROVAL_CONFIRMED"

    # Reuse the deterministic mechanical evaluator for explicit state.* conditions.
    if normalized.startswith("state."):
        status, reason = evaluate_mechanical_condition(normalized, state)
        return status != "blocked" or reason.startswith("mechanical condition evaluated"), status == "passed", reason

    equality = re.match(r"^([A-Za-z0-9_\.]+)\s*==\s*(.+)$", normalized)
    if equality:
        path = equality.group(1)
        expected = _parse_literal(equality.group(2))
        exists, value, location = _get_source_or_state_path(source, state, path)
        # Missing boolean flags are treated as False only for explicit == true checks.
        if not exists and expected is True:
            return True, False, f"condition evaluated as absent boolean flag: {path}=missing; expected=True"
        if not exists:
            return False, False, f"condition path not found for deterministic assertion evaluator: {path}"
        return True, value == expected, f"condition evaluated from {location}: {path}={value!r}; expected={expected!r}"

    # Bare identifiers are deterministic only if the package state/schema explicitly models them.
    if re.match(r"^[A-Za-z0-9_]+$", normalized):
        if normalized in state:
            value = state.get(normalized)
            return True, bool(value), f"condition evaluated from state flag: {normalized}={value!r}"
        return False, False, f"semantic condition is not mapped to deterministic state/source evaluator: {normalized}"

    return False, False, f"condition did not match deterministic assertion evaluator: {condition!r}"


def evaluate_assertions(source: dict[str, Any], state: dict[str, Any], gates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gate_status = {g["id"]: g["status"] for g in gates}
    results: list[dict[str, Any]] = []
    for assertion in source.get("assertions", []) or []:
        condition = assertion.get("condition", "")
        polarity = assertion.get("polarity")
        evaluated, condition_truth, reason = evaluate_assertion_condition(condition, source, state, gate_status)
        evaluation_mode = "behavioral" if evaluated else "structural_only"
        if not evaluated:
            status = "not_evaluated"
        elif polarity == "not":
            status = "violation" if condition_truth else "passed"
        elif polarity == "must":
            status = "passed" if condition_truth else "violation"
        else:
            status = "not_evaluated"
            reason = f"unsupported assertion polarity: {polarity!r}"
        results.append({
            "id": assertion.get("id"),
            "polarity": polarity,
            "severity": assertion.get("severity"),
            "phase": assertion.get("phase"),
            "status": status,
            "evaluation_mode": evaluation_mode,
            "condition": condition,
            "condition_truth": condition_truth if evaluated else None,
            "reason": reason,
        })
    return results


def allowed_outputs(source: dict[str, Any], gate_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gate_status = {g["id"]: g["status"] for g in gate_results}
    output_results: list[dict[str, Any]] = []
    for output in source.get("outputs", []) or []:
        required = output.get("allowed_after", []) or []
        missing = [g for g in required if gate_status.get(g) != "passed"]
        output_results.append({
            "id": output.get("id"),
            "type": output.get("type"),
            "allowed": len(missing) == 0,
            "required_gates": required,
            "missing_or_not_passed_gates": missing,
        })
    return output_results


def run_package(package_path: str | Path, answers_path: str | Path | None = None, state_path: str | Path | None = None, csg_events_path: str | Path | None = None) -> dict[str, Any]:
    root, manifest, source, tests = load_package(package_path)
    runtime_dir = root / "runtime"
    snapshots_dir = runtime_dir / "state_snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    state = initial_state(source)
    if state_path:
        state.update(load_yaml(Path(state_path)))
    answers = load_yaml(Path(answers_path)) if answers_path else {}
    csg_proposals = load_yaml(Path(csg_events_path)) if csg_events_path else []
    if isinstance(csg_proposals, dict):
        csg_proposals = csg_proposals.get("events", [])

    run_id = f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    started_at = utc_now()
    initial = copy.deepcopy(state)
    csg_results = apply_csg_events(source, state, csg_proposals or [])
    csg_events = [event for result in csg_results for event in result.get("events", [])]
    answer_events = apply_answers(source, state, answers)
    gate_results = evaluate_gates(source, state)
    assertion_results = evaluate_assertions(source, state, gate_results)
    outputs = allowed_outputs(source, gate_results)

    trace = {
        "run_id": run_id,
        "mode": "run",
        "execution_mode": ((source.get("ordo") or {}).get("execution_mode")),
        "trace_source": "runtime_enforced",
        "started_at": started_at,
        "finished_at": utc_now(),
        "input": {
            "answers_file": str(answers_path) if answers_path else None,
            "state_file": str(state_path) if state_path else None,
            "csg_events_file": str(csg_events_path) if csg_events_path else None,
        },
        "state": {
            "initial": initial,
            "final": state,
            "diff": state_diff(initial, state),
        },
        "events": csg_events + answer_events,
        "csg_report": csg_results,
        "gate_report": gate_results,
        "assertion_report": assertion_results,
        "outputs": outputs,
        "violations": [a for a in assertion_results if a.get("status") == "violation"],
        "blocked_outputs": [o for o in outputs if not o.get("allowed")],
    }
    write_json(snapshots_dir / f"{run_id}_state_initial.json", initial)
    write_json(snapshots_dir / f"{run_id}_state_final.json", state)
    write_json(runtime_dir / "trace_log.json", trace)
    write_json(root / "reports" / "run_report.json", trace)
    return trace
