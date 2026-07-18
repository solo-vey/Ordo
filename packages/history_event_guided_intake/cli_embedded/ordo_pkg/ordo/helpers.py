from __future__ import annotations

from pathlib import Path
from typing import Any
import copy
import json

from .loader import load_package, load_yaml
from .runtime import load_runtime_source, runtime_status
from .reporter import write_json
from .runtime_evidence import attach_report_digest
from .runner import initial_state, apply_answers, evaluate_gates, evaluate_assertions, allowed_outputs, state_diff
from .checkpoints import build_checkpoint_report, enrich_state_with_checkpoint


def _runtime_block_report(package_path: str | Path, *, out: str | Path | None, report_name: str) -> dict[str, Any] | None:
    status = runtime_status(package_path, require_ir=True)
    if status.get("status") == "ready":
        return None
    root = Path(package_path).resolve()
    try:
        root = load_package(package_path)[0]
    except Exception:
        pass
    report = {
        "status": "blocked",
        "helper_role": "deterministic_helper_for_ai_interpretation",
        "runtime_status": status,
        "issues": status.get("issues", []),
        "human_output_policy": "AI must report that runtime could not be loaded instead of inventing the next step.",
    }
    target = Path(out).resolve() if out else root / "reports" / report_name
    report = attach_report_digest(report)
    write_json(target, report)
    return report


def _extract_state_mapping(loaded: Any) -> dict[str, Any]:
    if not isinstance(loaded, dict):
        return {}
    embedded_state = loaded.get("state")
    if isinstance(embedded_state, dict):
        return embedded_state
    return loaded


def _load_state(
    source: dict[str, Any],
    state_path: str | Path | None = None,
    answers_path: str | Path | None = None,
    live_state_path: str | Path | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], str | None]:
    state = initial_state(source)
    state_source: str | None = None
    if state_path:
        loaded = load_yaml(Path(state_path))
        state.update(_extract_state_mapping(loaded))
        state_source = str(state_path)
    elif not answers_path and live_state_path and Path(live_state_path).exists():
        loaded = load_yaml(Path(live_state_path))
        live_state = _extract_state_mapping(loaded)
        if live_state:
            state.update(live_state)
            state_source = str(live_state_path)
    events: list[dict[str, Any]] = []
    if answers_path:
        answers = load_yaml(Path(answers_path))
        if isinstance(answers, dict):
            if isinstance(answers.get("answers"), dict):
                answers = answers["answers"]
            events = apply_answers(source, state, answers)
    return state, events, state_source


def _required_status(source: dict[str, Any], state: dict[str, Any]) -> list[dict[str, Any]]:
    required = ((source.get("contract") or {}).get("required") or [])
    result: list[dict[str, Any]] = []
    for field in required:
        value = state.get(field)
        present = value not in (None, False, "", [], {})
        result.append({
            "field": field,
            "present": present,
            "value_preview": value if isinstance(value, (str, int, float, bool)) or value is None else type(value).__name__,
        })
    return result


def validate_state(package_path: str | Path, *, state_path: str | Path | None = None, answers_path: str | Path | None = None, out: str | Path | None = None) -> dict[str, Any]:
    blocked = _runtime_block_report(package_path, out=out, report_name="state_validation_report.json")
    if blocked:
        return blocked
    root, manifest, source, _ir = load_runtime_source(package_path)
    state, events, state_source = _load_state(source, state_path, answers_path, root / "runtime" / "live_session_state.json")
    gate_results = evaluate_gates(source, state)
    assertion_results = evaluate_assertions(source, state, gate_results)
    outputs = allowed_outputs(source, gate_results)
    required = _required_status(source, state)
    missing_required = [r["field"] for r in required if not r["present"]]
    blocked_gates = [g for g in gate_results if g.get("status") == "blocked"]
    violations = [a for a in assertion_results if a.get("status") == "violation"]
    checkpoint = build_checkpoint_report(source, state)
    state = enrich_state_with_checkpoint(state, checkpoint)
    checkpoint_issues = checkpoint.get("issues", []) or []
    report = {
        "status": "passed" if not missing_required and not blocked_gates and not violations and not checkpoint_issues else "blocked",
        "helper_role": "deterministic_helper_for_ai_interpretation",
        "runtime_source": source.get("runtime_source", "source_yaml"),
        "human_output_policy": "ai_interprets_before_user",
        "inputs": {
            "state_file": state_source,
            "answers_file": str(answers_path) if answers_path else None,
        },
        "state": state,
        "events": events,
        "checkpoint": checkpoint,
        "earliest_incomplete_node": checkpoint.get("earliest_incomplete_node", ""),
        "open_required_fields": checkpoint.get("open_required_fields", []),
        "forward_allowed": checkpoint.get("forward_allowed", False),
        "checkpoint_issues": checkpoint_issues,
        "required_fields": required,
        "missing_required_fields": missing_required,
        "gate_report": gate_results,
        "blocked_gates": blocked_gates,
        "assertion_report": assertion_results,
        "violations": violations,
        "outputs": outputs,
    }
    target = Path(out).resolve() if out else root / "reports" / "state_validation_report.json"
    report = attach_report_digest(report)
    write_json(target, report)
    return report


def check_gate(package_path: str | Path, gate_id: str, *, state_path: str | Path | None = None, answers_path: str | Path | None = None, out: str | Path | None = None) -> dict[str, Any]:
    blocked = _runtime_block_report(package_path, out=out, report_name=f"gate_{gate_id}_check_report.json")
    if blocked:
        blocked["gate_id"] = gate_id
        return blocked
    root, manifest, source, _ir = load_runtime_source(package_path)
    state, events, state_source = _load_state(source, state_path, answers_path, root / "runtime" / "live_session_state.json")
    gates = evaluate_gates(source, state)
    gate = next((g for g in gates if g.get("id") == gate_id), None)
    checkpoint = build_checkpoint_report(source, state)
    report = {
        "status": "passed" if gate and gate.get("status") == "passed" and checkpoint.get("status") == "passed" else "blocked",
        "helper_role": "deterministic_helper_for_ai_interpretation",
        "gate_id": gate_id,
        "gate": gate,
        "checkpoint": checkpoint,
        "earliest_incomplete_node": checkpoint.get("earliest_incomplete_node", ""),
        "open_required_fields": checkpoint.get("open_required_fields", []),
        "forward_allowed": checkpoint.get("forward_allowed", False),
        "state": enrich_state_with_checkpoint(state, checkpoint),
        "state_source": state_source,
        "events": events,
    }
    target = Path(out).resolve() if out else root / "reports" / f"gate_{gate_id}_check_report.json"
    report = attach_report_digest(report)
    write_json(target, report)
    return report


def next_step(package_path: str | Path, *, state_path: str | Path | None = None, answers_path: str | Path | None = None, out: str | Path | None = None) -> dict[str, Any]:
    blocked = _runtime_block_report(package_path, out=out, report_name="next_step_report.json")
    if blocked:
        blocked["suggested_next_action"] = "runtime_not_ready"
        blocked["suggested_next_node"] = None
        return blocked
    root, manifest, source, _ir = load_runtime_source(package_path)
    state, events, state_source = _load_state(source, state_path, answers_path, root / "runtime" / "live_session_state.json")
    required = _required_status(source, state)
    missing = [r["field"] for r in required if not r["present"]]
    gates = evaluate_gates(source, state)
    first_blocked_gate = next((g for g in gates if g.get("status") == "blocked"), None)
    nodes = source.get("nodes", []) or []
    checkpoint = build_checkpoint_report(source, state)
    earliest = checkpoint.get("earliest_incomplete_node")
    # If next-step is reading the persisted runtime/live_session_state.json,
    # the branch-selected current_node is the active runtime target. This does
    # not apply to arbitrary --state files, where checkpoint discipline must
    # still report the earliest mandatory gap.
    live_state_selected_node = None
    if state_source and str(state_source).replace("\\", "/").endswith("runtime/live_session_state.json"):
        current_node = state.get("current_node")
        if current_node:
            table_entry = (checkpoint.get("checkpoint_table") or {}).get(str(current_node)) or {}
            if table_entry.get("status") in {"open", "incomplete"}:
                live_state_selected_node = str(current_node)
    if live_state_selected_node:
        earliest = live_state_selected_node
    suggested_node = earliest or (nodes[0].get("id") if nodes else None)
    status = "blocked" if checkpoint.get("node_merge_attempt_detected") else "generated"
    report = {
        "status": status,
        "helper_role": "deterministic_helper_for_ai_interpretation",
        "runtime_source": source.get("runtime_source", "source_yaml"),
        "human_output_policy": "ai_interprets_before_user",
        "missing_required_fields": missing,
        "first_blocked_gate": first_blocked_gate,
        "checkpoint": checkpoint,
        "earliest_incomplete_node": earliest or "",
        "open_required_fields": checkpoint.get("open_required_fields", []),
        "forward_allowed": checkpoint.get("forward_allowed", False),
        "suggested_next_node": suggested_node,
        "suggested_next_action": "collect_earliest_incomplete_node" if earliest else ("resolve_blocked_gate" if first_blocked_gate else "ready_for_ai_next_move"),
        "one_question_policy": "ask exactly one focused question unless allow_batch_confirmation is true",
        "state": enrich_state_with_checkpoint(state, checkpoint),
        "state_source": state_source,
        "events": events,
    }
    target = Path(out).resolve() if out else root / "reports" / "next_step_report.json"
    report = attach_report_digest(report)
    write_json(target, report)
    return report


def diff_state(package_path: str | Path, *, before: str | Path, after: str | Path, out: str | Path | None = None) -> dict[str, Any]:
    root, manifest, source, tests = load_package(package_path)
    before_state = load_yaml(Path(before))
    after_state = load_yaml(Path(after))
    if not isinstance(before_state, dict):
        before_state = {}
    if not isinstance(after_state, dict):
        after_state = {}
    diff = state_diff(before_state, after_state)
    report = {
        "status": "generated",
        "helper_role": "deterministic_helper_for_ai_interpretation",
        "before": str(before),
        "after": str(after),
        "diff": diff,
        "changed_fields": sorted(diff.keys()),
    }
    target = Path(out).resolve() if out else root / "reports" / "state_diff_report.json"
    report = attach_report_digest(report)
    write_json(target, report)
    return report


def explain_validation(package_path: str | Path, *, report_path: str | Path | None = None, out: str | Path | None = None) -> dict[str, Any]:
    root, manifest, source, tests = load_package(package_path)
    path = Path(report_path).resolve() if report_path else root / "reports" / "state_validation_report.json"
    raw = json.loads(path.read_text(encoding="utf-8")) if path.exists() else validate_state(package_path)
    missing = raw.get("missing_required_fields", [])
    blocked = raw.get("blocked_gates", [])
    violations = raw.get("violations", [])
    summary: list[str] = []
    if not missing and not blocked and not violations:
        summary.append("State is structurally ready for the next AI-led step.")
    if missing:
        summary.append("Missing required fields: " + ", ".join(missing) + ".")
    if blocked:
        summary.append("Blocked gates: " + ", ".join(str(g.get("id")) for g in blocked) + ".")
    if violations:
        summary.append("Assertion violations: " + ", ".join(str(v.get("id")) for v in violations) + ".")
    report = {
        "status": "generated",
        "helper_role": "deterministic_helper_for_ai_interpretation",
        "source_report": str(path),
        "ai_facing_summary": summary,
        "human_output_policy": "AI must convert this summary into plain language before showing it to the human user.",
    }
    target = Path(out).resolve() if out else root / "reports" / "validation_explanation_report.json"
    report = attach_report_digest(report)
    write_json(target, report)
    return report
