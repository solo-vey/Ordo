# BL-BENCH-054 — Execution Progress Status Output Governance

**Status:** DONE  
**Type:** Playbook execution / Driver observability improvement  
**Priority:** High

## Problem

During long playbook executions the user cannot reliably see which meaningful process steps have completed, which route the Driver selected, or whether the execution is progressing, correcting, blocked, or finished. Existing evidence logs are authoritative but are usually delivered only after the run and are too detailed for live chat progress.

## Goal

Add a compact, user-visible progress stream to playbook execution. After every meaningful completed step, the model emits one short status line without exposing private chain-of-thought, hidden reasoning, or confidential internal state.

## Canonical output format

```text
Крок <step_id_or_number> — <short observable action/result> — <status>[: <short factual reason>]
```

Examples:

```text
Крок T001 — перевірено вхідний пакет — PASS
Крок T035 — сформовано Passport v1 — COMPLETED
Крок T036 — Passport validation — FAIL: відсутні rollback assertions
Крок T037 — документ передано на виправлення — CORRECTION_REQUIRED
Крок T035 — Passport оновлено до v2 — IMPROVED
Крок T126 — виконання завершено — T_COMPLETED / GO
```

## Allowed statuses

- `PASS`
- `FAIL`
- `COMPLETED`
- `BLOCKED`
- `NO_CHANGE`
- `CORRECTION_REQUIRED`
- `INVALIDATED`
- `REGENERATED`
- `IMPROVED`
- `IMPROVEMENT_PLATEAU_REACHED`
- `SKIPPED_NOT_APPLICABLE`
- `T_COMPLETED / GO`
- `T_INPUT_BLOCKED / NO_GO`
- `T_SCENARIO_EXHAUSTED / NO_GO`

The status registry must be versioned and machine-readable. New statuses require a governed registry update.

## Rules

1. Emit a progress line only after a meaningful step reaches an observable state.
2. Do not emit hidden reasoning, chain-of-thought, speculative intent, or unsupported causal explanations.
3. The progress line may contain only: step identifier, concise observable action/result, canonical status, and an optional factual reason.
4. Group minor technical sub-actions under one meaningful playbook step to avoid chat flooding.
5. Repeated executions of the same step in a correction loop must preserve the same step ID and identify the new version/result.
6. Every emitted line must be bindable to Driver state, validator output, receipt, event-log record, or terminal decision.
7. A progress line is informational only and must never be treated as execution evidence by itself.
8. Authoritative evidence remains: Driver state, validator outputs, receipts, state snapshots, approvals, terminal records, and evidence packages.
9. A failed progress-output attempt must not mutate the business execution route.
10. The user-visible stream must remain concise and use the conversation language unless the launch contract specifies another language.

## Required process integration

Integrate the rule into:

- Driver execution policy;
- step completion handling;
- correction and regeneration loops;
- validation failure handling;
- improvement plateau handling;
- terminal route handling;
- execution logging;
- universal launch protocol.

## Required artifacts

- `EXECUTION_PROGRESS_OUTPUT_POLICY.yaml`
- `EXECUTION_PROGRESS_STATUS_REGISTRY.yaml`
- `schemas/execution_progress_event.schema.json`
- `templates/EXECUTION_PROGRESS_EVENT.template.json`
- a Driver/renderer implementation or normative runtime hook;
- positive and negative fixtures;
- acceptance-test report.

## Machine-readable event contract

Each progress event should minimally contain:

- `event_id`
- `run_id`
- `step_id`
- `step_sequence`
- `attempt`
- `short_summary`
- `status`
- `reason` (optional)
- `authoritative_evidence_refs`
- `emitted_at`
- `language`
- `informational_only: true`

## Gates

### G_PROGRESS_EVENT_SCHEMA

Every emitted event conforms to the schema and canonical status registry.

### G_PROGRESS_EVIDENCE_BINDING

Every event references at least one authoritative state or evidence record, except a launch-start notification explicitly allowed by policy.

### G_NO_REASONING_DISCLOSURE

The rendered line contains no hidden reasoning, chain-of-thought, internal deliberation, unsupported speculation, or sensitive implementation details.

### G_PROGRESS_CONCISENESS

The line follows the canonical one-line format and minor technical operations are not emitted individually.

### G_PROGRESS_TERMINAL_COHERENCE

The final progress line matches the authoritative terminal state and release disposition.

## Fail-closed behavior

A malformed or unsafe progress event is suppressed and logged as a telemetry defect. It must not change Driver state, approvals, validation decisions, or terminal routing.

Recommended telemetry status:

```text
PROGRESS_EVENT_SUPPRESSED
```

## Acceptance criteria

- Long runs expose concise progress after each meaningful step.
- Correction loops visibly show failure, correction, regeneration, improvement, revalidation, or plateau.
- No chain-of-thought or hidden reasoning is revealed.
- Every visible event is traceable to authoritative evidence.
- Final displayed status equals the authoritative terminal state.
- Chat volume remains bounded through step-level aggregation.
- Negative fixtures reject unbound, verbose, speculative, noncanonical, or terminal-incoherent messages.


## Implementation closure

Implemented in alpha.29 with nodes N098–N103, five hard gates, versioned policy/status registry, JSON schema, renderer, fixtures and acceptance tests.
