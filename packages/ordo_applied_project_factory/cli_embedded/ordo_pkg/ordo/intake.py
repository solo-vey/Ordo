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
from .reporter import write_json
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
    if not isinstance(loaded, dict):
        return {}
    embedded = loaded.get("state")
    if isinstance(embedded, dict):
        return embedded
    return loaded


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
    doc = {
        "status": "active" if current_node else "complete_or_gate_ready",
        "mode": "m59_4_live_runtime_session_state",
        "run_id": run_id,
        "current_node": current_node or "",
        "last_closed_node": last_closed_node,
        "state": state,
        "last_snapshot": last_snapshot,
        "last_snapshot_hash": last_snapshot_hash,
        "last_evidence_report": last_evidence_report,
        "last_evidence_digest": last_evidence_digest or {},
        "last_trace_path": last_trace_path,
        "last_trace_digest": last_trace_digest,
        "last_trace_step": last_trace_step,
        "updated_at": utc_now(),
        "resume_policy": "If --state is omitted, runtime helpers may resume from runtime/live_session_state.json.",
    }
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
    nodes = {n.get("id"): n for n in source.get("nodes", []) or []}
    node = nodes.get(node_id)
    run_id = str(live_session.get("run_id") or f"LIVE-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")

    if not has_chain_snapshots(root):
        write_session_snapshot(root, state, node_id="000_initial", action="initial_state", status="passed")

    checkpoint_before = build_checkpoint_report(source, state)
    # Branch-aware incremental runtime sessions resume from
    # runtime/live_session_state.json. In that specific persisted runtime
    # context, `current_node` is the authoritative next submit target.
    # For arbitrary user-supplied state files we keep the older checkpoint
    # discipline: earliest incomplete mandatory node wins.
    live_current = state.get("current_node") if isinstance(live_session, dict) and live_session else None
    expected_node = str(live_current) if live_current else (checkpoint_before.get("earliest_incomplete_node") or (node_id if node else ""))
    issues: list[dict[str, Any]] = []
    status = "passed"
    next_target: str | None = None
    diff: dict[str, Any] = {}
    matched = False

    if not node:
        status = "blocked"
        issues.append({"severity": "error", "code": "ORDO-INTAKE-001", "message": f"node not found: {node_id}", "location": node_id})
    elif expected_node and node_id != expected_node:
        status = "blocked"
        issues.append({"severity": "error", "code": "ORDO-INTAKE-002", "message": "submit attempted for a node other than earliest incomplete node", "location": node_id, "expected_node": expected_node})
    else:
        matched = _is_answer_matched(node, answer)
        if not matched:
            status = "blocked"
            issues.append({"severity": "error", "code": "ORDO-INTAKE-003", "message": "answer did not match node contract", "location": node_id, "allowed_answers": node.get("allowed_answers") or []})
        else:
            next_target, diff = _apply_node_answer(node, answer, state)
            answered = state.setdefault("answered_questions", [])
            if isinstance(answered, list):
                answered.append({"node": node_id, "answer": _parse_answer(answer, node.get("answer_type")), "closed_at": utc_now()})
            state["last_closed_node"] = node_id
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
    live_session_file = ""
    if status == "passed":
        live_session_file = _write_live_session_state(
            root,
            run_id=run_id,
            state=state,
            current_node=next_target or "",
            last_closed_node=node_id,
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
        "snapshot": _rel(root, snapshot_path),
        "session_chain": chain_meta,
        "issues": issues,
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

        if current_node.startswith("STOP"):
            trace["events"].append({"type": "stopped", "target": current_node})
            break

        node = nodes.get(current_node)
        if not node:
            trace["events"].append({"type": "error", "error": "node_not_found", "node": current_node})
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
                current_node = None
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
        if current_node is None:
            break
        if not matched:
            exhausted = ((node.get("on_unmatched_input") or {}).get("on_exhausted") or {})
            trace["events"].append({
                "type": "clarify_exhausted",
                "node": current_node,
                "attempts": attempt,
                "action": exhausted.get("action", "escalate_to_human"),
                "reason": exhausted.get("reason"),
            })
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
        "status": "passed" if not [a for a in assertion_results if a.get("status") == "violation"] else "failed",
    })
    trace = attach_report_digest(trace)
    write_json(runtime_dir / "intake_trace_log.json", trace)
    write_json(root / "reports" / "intake_report.json", trace)
    return trace
