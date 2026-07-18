# 019. Execution Logging

**Backlog task:** `BL-BENCH-019`  
**Status:** implemented evidence contract

## 1. Purpose

Create append-only evidence sufficient to reconstruct disclosure, decisions, corrections, state transitions, artifact versions and terminal routing without relying on chat memory.

## 2. Log format

Canonical format: UTF-8 JSON Lines, one event per line. Events are append-only and ordered by monotonically increasing `sequence`.

Mandatory common fields:

```text
schema_version
attempt_id
sequence
timestamp
event_type
actor
visibility_class
correlation_id
payload
previous_event_hash
event_hash
```

## 3. Required event types

- `ATTEMPT_STARTED`;
- `PREFLIGHT_PASSED`;
- `DRIVER_PROMPT_ISSUED`;
- `EXECUTOR_RESPONSE_RECEIVED`;
- `FACT_DISCLOSED`;
- `FACT_STATUS_CHANGED`;
- `STATE_TRANSITION`;
- `ARTIFACT_CREATED`;
- `ARTIFACT_REVISED`;
- `ARTIFACT_INVALIDATED`;
- `APPROVAL_RECORDED`;
- `APPROVAL_INVALIDATED`;
- `CORRECTION_APPLIED`;
- `DRIVER_DECISION`;
- `TERMINAL_CANDIDATE`;
- `TERMINAL_CONFIRMED`;
- `ATTEMPT_SEALED`.

## 4. Correction and version rules

A correction never edits an old event. It appends a correction event referencing affected event IDs, facts, approvals and artifact versions. Superseded evidence remains readable but cannot be treated as current.

Every artifact record includes logical artifact ID, version, digest, status and provenance. Approval is bound to the exact artifact version/digest.

## 5. Visibility

The master log may contain mixed visibility classes, but exported views must be filtered:

- executor view excludes Driver-private/evaluator-only payloads;
- Driver view excludes evaluator rubric and scores;
- evaluator view may open sealed Driver evidence only after attempt completion.

Redaction must preserve event identity, ordering and hash chain.

## 6. Completeness gate

A run cannot be sealed unless the log contains preflight success, all Driver prompts/responses, all fact disclosures/corrections, artifact lifecycle events and one confirmed terminal event.

## 7. Integrity

Hash chaining is required at contract level. A concrete runtime may use stronger signatures, but it may not omit sequence integrity or silently rewrite events.
