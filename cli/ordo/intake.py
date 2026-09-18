from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import copy
import json
import sys

from .loader import load_package, load_yaml
from .runtime import load_runtime_source
from .checkpoints import build_checkpoint_report, enrich_state_with_checkpoint
from .runtime_evidence import write_node_evidence, attach_report_digest, canonical_sha256
from .session_chain import has_chain_snapshots, write_session_snapshot
from .session_trace import append_session_trace_step
from .manual_run_journey import record_intake_event
from .transition_provenance import validate_node_entry, build_node_context_envelope
from .input_contract import evaluate_input_submission
from .analyst_interaction import evaluate_analyst_submission
from .reporter import write_json
from .runtime_context import (
    build_live_session,
    runtime_from_session,
    split_business_state,
    state_from_session,
    validate_live_session,
)
from .runner import (
    initial_state,
    state_diff,
    set_path,
    evaluate_gates,
    evaluate_assertions,
    allowed_outputs,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_answer(raw: Any, answer_type: str | None) -> Any:
    if answer_type == "list" and isinstance(raw, str):
        return [part.strip() for part in raw.split(",") if part.strip()]
    return raw


def _answer_from_map(answers: dict[str, Any], node_id: str, attempt: int) -> tuple[bool, Any]:
    if node_id not in answers:
        return False, None
    value = answers[node_id]
    if isinstance(value, list) and value and not all(isinstance(x, str) for x in value):
        # Treat list of non-string objects as attempts only if explicitly nested.
        pass
    if isinstance(value, dict) and "attempts" in value:
        attempts = value.get("attempts") or []
        if attempt < len(attempts):
            return True, attempts[attempt]
        return False, None
    return True, value


def _prompt_for_answer(node: dict[str, Any], attempt: int) -> Any:
    print()
    print(f"[{node.get('id')}] {node.get('question')}")
    allowed = node.get("allowed_answers")
    if allowed:
        print("Allowed:", ", ".join(str(x) for x in allowed))
    if attempt > 0:
        clarify = node.get("on_unmatched_input") or {}
        strategy = clarify.get("strategy", "rephrase_and_narrow")
        print(f"Clarify ({strategy}): please answer in the expected format.")
    return input("> ")


def _apply_node_answer(node: dict[str, Any], answer: Any, state: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    before = copy.deepcopy(state)
    on_answer = node.get("on_answer") or {}
    next_target: str | None = None
    update: dict[str, Any] = {}

    if isinstance(on_answer, dict) and "update_state" in on_answer:
        update = on_answer.get("update_state") or {}
        next_target = on_answer.get("next")
    elif isinstance(on_answer, dict):
        matched_key = None
        for key in on_answer.keys():
            if str(key).lower() == str(answer).lower():
                matched_key = key
                break
        if matched_key is not None:
            branch = on_answer.get(matched_key) or {}
            update = branch.get("update_state") or {}
            next_target = branch.get("next")

    parsed_answer = _parse_answer(answer, node.get("answer_type"))
    for key, value in update.items():
        set_path(state, key, parsed_answer if value == "$answer" else value)
    return next_target, state_diff(before, state)


def _failure_route(node: dict[str, Any], failure_kind: str) -> dict[str, Any] | None:
    """Return the explicitly authored route for one recoverable failure kind."""
    for route in node.get("failure_routes", []) or []:
        if isinstance(route, dict) and route.get("kind") == failure_kind:
            return route
    return None


def _is_answer_matched(node: dict[str, Any], answer: Any) -> bool:
    allowed = node.get("allowed_answers")
    if not allowed:
        # For free_text/list nodes, empty answer is treated as unmatched.
        return answer not in (None, "", [])
    return str(answer).lower() in {str(x).lower() for x in allowed}


def _load_runtime_package(package_path: str | Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    # Runtime Mode must use compiled IR as source of truth. If compiled IR is not
    # available yet in a dev package, fall back to load_package so legacy authoring
    # tests can still expose the underlying runtime-status failure through helpers.
    try:
        root, manifest, source, _ir = load_runtime_source(package_path)
        return root, manifest, source
    except Exception:
        root, manifest, source, _tests = load_package(package_path)
        source = dict(source)
        source.setdefault("runtime_source", "source_yaml")
        return root, manifest, source


def _load_state_for_submit(root: Path, source: dict[str, Any], state_path: str | Path | None) -> tuple[dict[str, Any], str | None, dict[str, Any]]:
    state = initial_state(source)
    if state_path:
        loaded = load_yaml(Path(state_path))
        state.update(_state_from_loaded_mapping(loaded))
        return state, str(state_path), {}
    live = _load_live_session(root)
    live_state = _state_from_loaded_mapping(live)
    if live_state:
        state.update(live_state)
        return state, _rel(root, _live_session_path(root)), live
    return state, None, {}


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path)


def _state_from_loaded_mapping(loaded: Any) -> dict[str, Any]:
    return state_from_session(loaded)


def _live_session_path(root: Path) -> Path:
    return root / "runtime" / "live_session_state.json"


def _load_live_session(root: Path) -> dict[str, Any]:
    path = _live_session_path(root)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _write_live_session_state(
    root: Path,
    *,
    source: dict[str, Any],
    run_id: str,
    state: dict[str, Any],
    current_node: str,
    last_closed_node: str,
    last_snapshot: str,
    last_snapshot_hash: str,
    last_evidence_report: str,
    last_evidence_digest: dict[str, Any] | None,
    last_trace_path: str = "",
    last_trace_digest: str = "",
    last_trace_step: int | None = None,
) -> str:
    business_state, legacy_runtime = split_business_state(state)
    doc = build_live_session(
        root, source,
        run_id=run_id,
        business_state=business_state,
        status="active" if current_node else "complete_or_gate_ready",
        runtime={
            **legacy_runtime,
            "current_node": current_node or "",
            "last_closed_node": last_closed_node,
            "updated_at": utc_now(),
        },
        evidence={
            "last_snapshot": last_snapshot,
            "last_snapshot_hash": last_snapshot_hash,
            "last_evidence_report": last_evidence_report,
            "last_evidence_digest": last_evidence_digest or {},
            "last_trace_path": last_trace_path,
            "last_trace_digest": last_trace_digest,
            "last_trace_step": last_trace_step,
        },
        resume_policy="If --state is omitted, runtime helpers may resume only from a source-bound runtime/live_session_state.json.",
    )
    target = _live_session_path(root)
    write_json(target, doc)
    return _rel(root, target)


def submit_intake_node(
    package_path: str | Path,
    *,
    node_id: str,
    answer: Any,
    state_path: str | Path | None = None,
    out: str | Path | None = None,
) -> dict[str, Any]:
    root, manifest, source = _load_runtime_package(package_path)
    runtime_dir = root / "runtime"
    snapshots_dir = runtime_dir / "state_snapshots"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    state, input_state_file, live_session = _load_state_for_submit(root, source, state_path)
    state_before_journey = copy.deepcopy(state)
    nodes = {n.get("id"): n for n in source.get("nodes", []) or []}
    node = nodes.get(node_id)
    live_runtime = runtime_from_session(live_session)
    run_id = str(live_runtime.get("run_id") or f"LIVE-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")

    if not has_chain_snapshots(root):
        write_session_snapshot(root, state, node_id="000_initial", action="initial_state", status="passed")

    checkpoint_before = build_checkpoint_report(source, state)
    # Branch-aware incremental runtime sessions resume from
    # runtime/live_session_state.json. In that specific persisted runtime
    # context, `current_node` is the authoritative next submit target.
    # For arbitrary user-supplied state files we keep the older checkpoint
    # discipline: earliest incomplete mandatory node wins.
    context_issues = validate_live_session(root, source, live_session) if live_session else []
    live_current = live_runtime.get("current_node") if live_session else None
    expected_node = str(live_current) if live_current else (checkpoint_before.get("earliest_incomplete_node") or (node_id if node else ""))
    issues: list[dict[str, Any]] = []
    status = "passed"
    next_target: str | None = None
    diff: dict[str, Any] = {}
    matched = False

    if context_issues:
        status = "blocked"
        issues.extend(context_issues)
    elif not node:
        status = "blocked"
        issues.append({"severity": "error", "code": "ORDO-INTAKE-001", "message": f"node not found: {node_id}", "location": node_id})
    elif expected_node and node_id != expected_node:
        status = "blocked"
        issues.append({"severity": "error", "code": "ORDO-INTAKE-002", "message": "submit attempted for a node other than earliest incomplete node", "location": node_id, "expected_node": expected_node})
    else:
        previous_node_id = (
            live_runtime.get("previous_node_id")
            or live_runtime.get("last_closed_node")
            or state.get("previous_node_id")
            or state.get("last_closed_node")
        )
        entry_mode = "resume" if live_session else ("root" if not previous_node_id else "transition")
        provenance = validate_node_entry(source, target_node_id=node_id, previous_node_id=previous_node_id, entry_mode=entry_mode)
        if provenance.get("status") != "passed":
            status = "blocked"
            issues.extend(provenance.get("issues", []))
        submission = evaluate_input_submission(source, node, answer) if status == "passed" else {"status": status, "answer": answer, "issues": []}
        answer = submission.get("answer", answer)
        if submission.get("status") != "passed":
            status = "clarification_required" if submission.get("status") == "clarification_required" else "blocked"
            next_target = submission.get("next_node")
            issues.extend(submission.get("issues", []))
        elif status == "passed":
            interaction = evaluate_analyst_submission(source, node, answer)
            answer = interaction.get("answer", answer)
            if interaction.get("status") != "passed":
                status = "clarification_required"
                next_target = interaction.get("next_node")
                issues.extend(interaction.get("issues", []))
        matched = status == "passed" and _is_answer_matched(node, answer)
        if status == "passed" and not matched:
            status = "blocked"
            issues.append({"severity": "error", "code": "ORDO-INTAKE-003", "message": "answer did not match node contract", "location": node_id, "allowed_answers": node.get("allowed_answers") or []})
        elif status == "passed":
            next_target, diff = _apply_node_answer(node, answer, state)
            answered = state.setdefault("answered_questions", [])
            if isinstance(answered, list):
                answered.append({"node": node_id, "answer": _parse_answer(answer, node.get("answer_type")), "closed_at": utc_now()})
            # Control-flow fields are persisted in runtime_context, never in
            # business state.  Keep them transient here for existing checkpoint
            # and evidence helpers, then split them before session persistence.
            state["last_closed_node"] = node_id
            state["previous_node_id"] = node_id
            state["current_node"] = next_target or ""

    checkpoint_after = build_checkpoint_report(source, state)
    state = enrich_state_with_checkpoint(state, checkpoint_after)
    snapshot_path, chained_state, chain_meta = write_session_snapshot(
        root,
        state,
        node_id=node_id,
        action="intake_submit",
        answer=_parse_answer(answer, node.get("answer_type") if node else None),
        status=status,
        extra={"run_id": run_id},
    )
    state = chained_state
    evidence = write_node_evidence(
        root,
        run_id=run_id,
        step_index=1,
        node_id=node_id,
        action="intake_submit",
        status=status,
        state=state,
        state_diff=diff,
        answer=_parse_answer(answer, node.get("answer_type") if node else None),
        next_node=next_target,
        checkpoint=checkpoint_after,
        snapshot_path=_rel(root, snapshot_path),
        extra={"issues": issues, "matched": matched, "expected_node": expected_node},
    )
    trace = append_session_trace_step(
        root,
        run_id=run_id,
        node_id=node_id,
        action="intake_submit",
        status=status,
        answer=_parse_answer(answer, node.get("answer_type") if node else None),
        next_node=next_target,
        evidence_path=str(evidence.get("evidence_path") or ""),
        snapshot_path=_rel(root, snapshot_path),
        snapshot_hash=str(chain_meta.get("snapshot_hash") or ""),
    )
    if evidence.get("evidence_path"):
        evidence_file = root / str(evidence.get("evidence_path"))
        if evidence_file.exists():
            evidence_doc = json.loads(evidence_file.read_text(encoding="utf-8"))
            evidence_doc["session_trace"] = {
                "path": trace.get("path"),
                "format": trace.get("format"),
                "step_index": trace.get("step_index"),
                "step_id": trace.get("step_id"),
                "trace_digest": trace.get("digest"),
                "trace_fragment": trace.get("fragment"),
            }
            evidence_doc["evidence_digest"] = {
                "algorithm": "sha256",
                "scope": "canonical_json_without_evidence_digest",
                "value": canonical_sha256({k: v for k, v in evidence_doc.items() if k != "evidence_digest"}),
            }
            write_json(evidence_file, evidence_doc)
            evidence_doc["evidence_path"] = str(evidence.get("evidence_path"))
            evidence = evidence_doc
    journey = record_intake_event(
        root, run_id=run_id, node=node or {"id": node_id}, answer=_parse_answer(answer, node.get("answer_type") if node else None),
        status=status, state_before=state_before_journey, state_after=state, state_diff=diff, next_node=next_target,
        issues=issues, trace=trace, snapshot_path=_rel(root, snapshot_path), snapshot_hash=str(chain_meta.get("snapshot_hash") or ""),
    )
    live_session_file = ""
    if status in {"passed", "clarification_required"}:
        if status == "clarification_required" and next_target:
            # A rejected semantic draft or ambiguous answer never writes business
            # state. It does persist the deterministic retry checkpoint.
            state["current_node"] = next_target
        live_session_file = _write_live_session_state(
            root,
            source=source,
            run_id=run_id,
            state=state,
            current_node=next_target or (node_id if status == "clarification_required" else ""),
            last_closed_node=node_id if status == "passed" else str(live_runtime.get("last_closed_node") or ""),
            last_snapshot=_rel(root, snapshot_path),
            last_snapshot_hash=str(chain_meta.get("snapshot_hash") or ""),
            last_evidence_report=str(evidence.get("evidence_path") or ""),
            last_evidence_digest=evidence.get("evidence_digest") if isinstance(evidence.get("evidence_digest"), dict) else {},
            last_trace_path=str(trace.get("path") or ""),
            last_trace_digest=str(trace.get("digest") or ""),
            last_trace_step=int(trace.get("step_index") or 0),
        )

    report = {
        "status": status,
        "mode": "runtime_incremental_intake_submit",
        "runtime_source": source.get("runtime_source", "source_yaml"),
        "run_id": run_id,
        "input": {"state_file": input_state_file, "submitted_node": node_id},
        "node_id": node_id,
        "answer": _parse_answer(answer, node.get("answer_type") if node else None),
        "matched": matched,
        "next_node": next_target or "",
        "state": state,
        "state_diff": diff,
        "checkpoint_before": checkpoint_before,
        "checkpoint": checkpoint_after,
        "evidence_report": evidence.get("evidence_path"),
        "evidence_digest": evidence.get("evidence_digest"),
        "session_trace": {
            "path": trace.get("path"),
            "format": trace.get("format"),
            "step_index": trace.get("step_index"),
            "step_id": trace.get("step_id"),
            "trace_digest": trace.get("digest"),
            "trace_fragment": trace.get("fragment"),
        },
        "live_session_state": live_session_file,
        "manual_run_journey": journey,
        "snapshot": _rel(root, snapshot_path),
        "session_chain": chain_meta,
        "issues": issues,
        "node_context_envelope": build_node_context_envelope(source, state, node_id) if node else {},
        "human_output_policy": "AI must report evidence_report path and SHA-256 digest before asking the next question.",
    }
    report = attach_report_digest(report)
    target = Path(out).resolve() if out else root / "reports" / "intake_submit_report.json"
    write_json(target, report)
    return report


def guided_intake(
    package_path: str | Path,
    answers_path: str | Path | None = None,
    start_node: str | None = None,
    non_interactive: bool = False,
) -> dict[str, Any]:
    root, manifest, source = _load_runtime_package(package_path)
    runtime_dir = root / "runtime"
    snapshots_dir = runtime_dir / "state_snapshots"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    answers = load_yaml(Path(answers_path)) if answers_path else {}

    # M60.3.2 runtime automation safety: a bare guided intake without
    # --answers/--non-interactive must not block indefinitely on input() when
    # stdin is not a TTY, which is the common subprocess/agent execution mode.
    if not answers_path and not non_interactive and not sys.stdin.isatty():
        report = {
            "status": "failed",
            "mode": "guided_intake_fail_fast",
            "reason": "no_answers_and_not_interactive_and_no_tty",
            "input": {
                "answers_file": None,
                "start_node": start_node,
                "non_interactive": non_interactive,
                "stdin_isatty": False,
            },
            "issues": [
                {
                    "severity": "error",
                    "code": "ORDO-INTAKE-004",
                    "message": "Bare intake requires --answers, --non-interactive, or a TTY for interactive prompting.",
                    "location": "intake",
                }
            ],
            "automation_policy": "Runtime automation must use intake --submit, or guided intake with --answers --non-interactive. Bare interactive intake is only valid in a TTY.",
        }
        report = attach_report_digest(report)
        write_json(root / "reports" / "intake_report.json", report)
        return report

    state = initial_state(source)
    nodes = {n.get("id"): n for n in source.get("nodes", []) or []}
    if not nodes:
        raise ValueError("No nodes defined in package source")
    current_node = start_node or (source.get("nodes") or [])[0].get("id")

    run_id = f"INTAKE-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    trace: dict[str, Any] = {
        "run_id": run_id,
        "mode": "guided_intake",
        "execution_mode": ((source.get("ordo") or {}).get("execution_mode")),
        "trace_source": "runtime_enforced",
        "started_at": utc_now(),
        "input": {
            "answers_file": str(answers_path) if answers_path else None,
            "start_node": current_node,
            "non_interactive": non_interactive,
        },
        "events": [],
        "state_snapshots": [],
    }

    visited_steps = 0
    max_steps = 100
    gate_results: list[dict[str, Any]] = []
    flow_status = "passed"

    initial_snapshot, initial_state_chained, initial_chain = write_session_snapshot(root, state, node_id="000_initial", action="initial_state", status="passed", extra={"run_id": run_id})
    state = initial_state_chained
    trace["state_snapshots"].append(str(initial_snapshot.relative_to(root)).replace("\\", "/"))
    trace["session_chain_start"] = initial_chain

    while current_node and visited_steps < max_steps:
        visited_steps += 1
        if current_node.startswith("G_"):
            # Evaluate all gates to keep output dependency status consistent, then log selected gate.
            all_gate_results = evaluate_gates(source, state)
            gate_results = all_gate_results
            selected = next((g for g in all_gate_results if g.get("id") == current_node), None)
            snapshot_path, chained_state, chain_meta = write_session_snapshot(
                root,
                state,
                node_id=current_node,
                action="gate_evaluated",
                status="passed" if selected and selected.get("status") == "passed" else "blocked",
                extra={"run_id": run_id},
            )
            state = chained_state
            evidence = write_node_evidence(
                root,
                run_id=run_id,
                step_index=visited_steps,
                node_id=current_node,
                action="gate_evaluated",
                status="passed" if selected and selected.get("status") == "passed" else "blocked",
                state=state,
                gate=selected,
                next_node="",
                snapshot_path=str(snapshot_path.relative_to(root)).replace("\\", "/"),
            )
            trace["events"].append({"type": "gate_evaluated", "gate": current_node, "result": selected, "evidence_report": evidence.get("evidence_path"), "evidence_digest": evidence.get("evidence_digest"), "session_chain": chain_meta})
            trace["state_snapshots"].append(str(snapshot_path.relative_to(root)).replace("\\", "/"))
            break

        node = nodes.get(current_node)
        if not node:
            trace["events"].append({"type": "error", "error": "node_not_found", "node": current_node})
            break
        if current_node.startswith("STOP") or node.get("terminal") is True:
            trace["events"].append({"type": "stopped" if current_node.startswith("STOP") else "terminal_reached", "target": current_node})
            state["current_node"] = current_node
            flow_status = "stopped" if current_node.startswith("STOP") else "passed"
            break

        max_attempts = int(((node.get("on_unmatched_input") or {}).get("max_attempts") or 0))
        attempt = 0
        answer = None
        matched = False
        while attempt <= max_attempts:
            found, scripted = _answer_from_map(answers, current_node, attempt)
            if found:
                answer = scripted
            elif non_interactive:
                trace["events"].append({"type": "missing_answer", "node": current_node, "action": "block"})
                state["current_node"] = current_node
                flow_status = "blocked"
                break
            else:
                answer = _prompt_for_answer(node, attempt)
            matched = _is_answer_matched(node, answer)
            if matched:
                break
            trace["events"].append({
                "type": "clarify_requested",
                "op": "CLARIFY.REQUEST",
                "node": current_node,
                "attempt": attempt + 1,
                "answer": answer,
                "on_unmatched_input": node.get("on_unmatched_input"),
            })
            attempt += 1
        if not matched:
            exhausted = ((node.get("on_unmatched_input") or {}).get("on_exhausted") or {})
            route = _failure_route(node, "input")
            trace["events"].append({
                "type": "clarify_exhausted",
                "node": current_node,
                "attempts": attempt,
                "action": exhausted.get("action", "escalate_to_human"),
                "reason": exhausted.get("reason"),
            })
            if route and route.get("classification") in {"recoverable", "terminal"} and isinstance(route.get("next"), str):
                next_target = route["next"]
                state["last_closed_node"] = current_node
                state["current_node"] = next_target
                snapshot_path, chained_state, chain_meta = write_session_snapshot(
                    root, state, node_id=current_node, action="input_failure_routed", answer={"attempts": attempt}, status="passed", extra={"run_id": run_id, "failure_route": route},
                )
                state = chained_state
                evidence = write_node_evidence(
                    root, run_id=run_id, step_index=visited_steps, node_id=current_node, action="input_failure_routed", status="passed", state=state,
                    answer={"attempts": attempt}, next_node=next_target, snapshot_path=str(snapshot_path.relative_to(root)).replace("\\", "/"), extra={"failure_route": route},
                )
                trace["events"].append({
                    "type": "recoverable_failure_routed" if route["classification"] == "recoverable" else "terminal_failure_routed",
                    "node": current_node, "failure_kind": "input", "classification": route["classification"], "next": next_target,
                    "evidence_report": evidence.get("evidence_path"), "evidence_digest": evidence.get("evidence_digest"), "session_chain": chain_meta,
                })
                trace["state_snapshots"].append(str(snapshot_path.relative_to(root)).replace("\\", "/"))
                current_node = next_target
                continue
            # No declared route is a blocked checkpoint, not a hidden terminal
            # transition. A user can retry from the same active node later.
            state["current_node"] = current_node
            flow_status = "blocked"
            break

        interaction = evaluate_analyst_submission(source, node, answer)
        answer = interaction.get("answer", answer)
        if interaction.get("status") != "passed":
            next_target = interaction.get("next_node")
            trace["events"].append({
                "type": interaction.get("status"),
                "node": current_node,
                "next": next_target,
                "issues": interaction.get("issues", []),
                "state_mutation": False,
            })
            if isinstance(next_target, str) and next_target:
                state["current_node"] = next_target
                current_node = next_target
                continue
            state["current_node"] = current_node
            flow_status = "blocked"
            break

        node_id_for_event = current_node
        next_target, diff = _apply_node_answer(node, answer, state)
        answered = state.setdefault("answered_questions", [])
        if isinstance(answered, list):
            answered.append({"node": node_id_for_event, "answer": _parse_answer(answer, node.get("answer_type")), "closed_at": utc_now()})
        state["last_closed_node"] = node_id_for_event
        state["current_node"] = next_target or ""
        snapshot_path, chained_state, chain_meta = write_session_snapshot(
            root,
            state,
            node_id=node_id_for_event,
            action="node_answered",
            answer=_parse_answer(answer, node.get("answer_type")),
            status="passed",
            extra={"run_id": run_id},
        )
        state = chained_state
        evidence = write_node_evidence(
            root,
            run_id=run_id,
            step_index=visited_steps,
            node_id=node_id_for_event,
            action="node_answered",
            status="passed",
            state=state,
            state_diff=diff,
            answer=_parse_answer(answer, node.get("answer_type")),
            next_node=next_target,
            snapshot_path=str(snapshot_path.relative_to(root)).replace("\\", "/"),
        )
        trace["events"].append({
            "type": "node_answered",
            "node": node_id_for_event,
            "answer": _parse_answer(answer, node.get("answer_type")),
            "next": next_target,
            "state_diff": diff,
            "evidence_report": evidence.get("evidence_path"),
            "evidence_digest": evidence.get("evidence_digest"),
            "session_chain": chain_meta,
        })
        trace["state_snapshots"].append(str(snapshot_path.relative_to(root)).replace("\\", "/"))
        current_node = next_target

    if not gate_results:
        gate_results = evaluate_gates(source, state)
    assertion_results = evaluate_assertions(source, state, gate_results)
    outputs = allowed_outputs(source, gate_results)
    trace.update({
        "finished_at": utc_now(),
        "state": state,
        "gate_report": gate_results,
        "assertion_report": assertion_results,
        "outputs": outputs,
        "violations": [a for a in assertion_results if a.get("status") == "violation"],
        "blocked_outputs": [o for o in outputs if not o.get("allowed")],
        "status": "failed" if [a for a in assertion_results if a.get("status") == "violation"] else flow_status,
    })
    trace = attach_report_digest(trace)
    write_json(runtime_dir / "intake_trace_log.json", trace)
    write_json(root / "reports" / "intake_report.json", trace)
    return trace
