from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from antipattern_runtime_binding import build_adapter


@dataclass(frozen=True)
class HookExecutionResult:
    decision: str
    next_target: str | None
    blocked: bool
    advisory: bool
    hook_id: str
    report: dict[str, Any]


def _get_path(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split('.'):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _set_path(data: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split('.')
    current = data
    for part in parts[:-1]:
        nxt = current.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            current[part] = nxt
        current = nxt
    current[parts[-1]] = value


def _append_unique(data: dict[str, Any], path: str, values: Iterable[Any], *, key: str | None = None) -> None:
    existing = _get_path(data, path)
    if not isinstance(existing, list):
        existing = []
    output = list(existing)
    seen = set()
    if key:
        seen = {item.get(key) for item in output if isinstance(item, dict)}
    else:
        seen = {json.dumps(item, sort_keys=True, ensure_ascii=False, default=str) for item in output}
    for item in values:
        marker = item.get(key) if key and isinstance(item, dict) else json.dumps(item, sort_keys=True, ensure_ascii=False, default=str)
        if marker not in seen:
            output.append(item)
            seen.add(marker)
    _set_path(data, path, output)


def _project_state(state: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    projected: dict[str, Any] = {}
    for field in fields:
        value = _get_path(state, field)
        _set_path(projected, field, copy.deepcopy(value))
    return projected


def _evidence_ref(hook: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps(
        {
            'hook_id': hook['hook_id'],
            'source_id': hook['source_id'],
            'decision': report.get('decision'),
            'findings': [f.get('finding_id') for f in report.get('findings', [])],
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    report_payload = json.dumps(report, sort_keys=True, ensure_ascii=False, default=str)
    return {
        'schema_version': 'ordo.antipattern_evidence_ref.v1',
        'evidence_type': 'ANTIPATTERN.EVIDENCE_REF',
        'evidence_id': 'APE-' + hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16].upper(),
        'hook_id': hook['hook_id'],
        'source_id': hook['source_id'],
        'gate_id': report.get('gate_id'),
        'context_type': hook['context_type'],
        'decision': report.get('decision', 'block'),
        'finding_ids': sorted({f.get('finding_id') for f in report.get('findings', []) if f.get('matched') and f.get('finding_id')}),
        'report_digest': hashlib.sha256(report_payload.encode('utf-8')).hexdigest(),
        'recorded_at': datetime.now(timezone.utc).isoformat(),
    }


def _synthetic_fail_closed_report(hook: dict[str, Any], exc: Exception) -> dict[str, Any]:
    return {
        'schema_version': 'ordo.antipattern_gate_report.v1',
        'report_type': 'GATE.REPORT',
        'decision': 'block',
        'summary': {
            'total_findings': 0,
            'matched_findings': 0,
            'blocking_findings': 1,
            'advisory_findings': 0,
            'inconclusive_findings': 1,
            'highest_severity': 'critical',
        },
        'blocking_finding_ids': [],
        'advisory_finding_ids': [],
        'findings': [],
        'gate_id': 'ANTIPATTERN_RUNTIME_FAIL_CLOSED',
        'context_type': hook.get('context_type'),
        'source_id': hook.get('source_id'),
        'enabled_antipatterns': hook.get('enabled_antipattern_overrides', []),
        'runtime_error': f'{type(exc).__name__}: {exc}',
        'inconclusive_escalated_to_block': True,
    }


def execute_hook(
    *,
    package_root: str | Path,
    hook: dict[str, Any],
    state: dict[str, Any],
    normal_next_target: str | None,
    adapter: Any | None = None,
) -> HookExecutionResult:
    adapter = adapter or build_adapter(package_root)
    projection_fields = hook['input']['state_projection']
    projected_state = _project_state(state, projection_fields)

    try:
        report = adapter.evaluate_gate(
            state=projected_state,
            context_type=hook['context_type'],
            source_id=hook['source_id'],
            source_hash=_get_path(state, hook['input'].get('source_hash_ref') or '') if hook['input'].get('source_hash_ref') else None,
            enabled_antipattern_overrides=hook.get('enabled_antipattern_overrides'),
        )
    except Exception as exc:
        report = _synthetic_fail_closed_report(hook, exc)

    output = hook['output']
    _set_path(state, output['report_state_field'], report)
    _append_unique(state, output['findings_state_field'], report.get('findings', []), key='finding_id')
    _set_path(state, output['gate_status_state_field'], report.get('decision', 'block'))
    evidence = _evidence_ref(hook, report)
    _append_unique(state, output['evidence_refs_state_field'], [evidence], key='evidence_id')
    state['antipattern_last_hook_id'] = hook['hook_id']
    state['antipattern_last_context_type'] = hook['context_type']

    decision = report.get('decision', 'block')
    if decision == 'block' or decision == 'inconclusive':
        state['antipattern_repair_required'] = True
        state['antipattern_repair_target'] = hook['routing']['on_block']['repair_target']
        state['antipattern_blocked_transition_target'] = normal_next_target
        return HookExecutionResult(
            decision='block',
            next_target=hook['routing']['on_block']['repair_target'],
            blocked=True,
            advisory=False,
            hook_id=hook['hook_id'],
            report=report,
        )

    state['antipattern_repair_required'] = False
    state['antipattern_repair_target'] = None
    state['antipattern_blocked_transition_target'] = None
    if decision == 'allow_with_advisory':
        return HookExecutionResult(
            decision=decision,
            next_target=normal_next_target,
            blocked=False,
            advisory=True,
            hook_id=hook['hook_id'],
            report=report,
        )
    return HookExecutionResult(
        decision='allow',
        next_target=normal_next_target,
        blocked=False,
        advisory=False,
        hook_id=hook['hook_id'],
        report=report,
    )


def execute_node_hooks(
    *,
    package_root: str | Path,
    node: dict[str, Any],
    phase: str,
    state: dict[str, Any],
    normal_next_target: str | None,
    adapter: Any | None = None,
) -> dict[str, Any]:
    results: list[HookExecutionResult] = []
    next_target = normal_next_target
    for hook in node.get('antipattern_hooks', []) or []:
        if hook.get('phase') != phase:
            continue
        result = execute_hook(
            package_root=package_root,
            hook=hook,
            state=state,
            normal_next_target=next_target,
            adapter=adapter,
        )
        results.append(result)
        next_target = result.next_target
        if result.blocked:
            break
    return {
        'decision': 'block' if any(r.blocked for r in results) else 'allow_with_advisory' if any(r.advisory for r in results) else 'allow',
        'next_target': next_target,
        'blocked': any(r.blocked for r in results),
        'advisory': any(r.advisory for r in results),
        'executed_hook_ids': [r.hook_id for r in results],
        'reports': [r.report for r in results],
    }
