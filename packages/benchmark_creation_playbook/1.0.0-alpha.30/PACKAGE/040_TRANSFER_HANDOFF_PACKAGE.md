# 040 — Transfer / Handoff Package

## Purpose

Provide a deterministic continuation package for another chat, model, analyst, or runtime without relying on hidden conversational memory.

## Handoff invariant

The receiver must be able to determine: what exists, what is authoritative, what is complete, what remains open, what must not be changed, and what the next safe action is.

## Required contents

1. `HANDOFF_README.md` — reading order and package map.
2. `CURRENT_STATE.md` — current version, completed epics, readiness, active constraints and known limitations.
3. `BACKLOG.md` — authoritative status ledger.
4. `NEXT_ACTION.md` — one bounded recommended next action.
5. `TRANSFER_PROMPT.md` — reusable receiver prompt with authority and no-downgrade rules.
6. Source-of-truth playbook files, Ordo source, registries, templates and schemas.
7. Validation report, checksum manifest and package inventory.
8. Open-risk register including unresolved `BL-BENCH-041`.

## Receiver preflight

The receiver must:

- verify all checksums;
- confirm the received version is not older than the active baseline;
- read `HANDOFF_README.md`, `CURRENT_STATE.md`, `BACKLOG.md` and `NEXT_ACTION.md` in that order;
- preserve immutable IDs and historical completion records;
- not mark open work complete without materialized evidence and validation;
- stop and report no-change on integrity failure.

## Handoff status

- `READY_FOR_TRANSFER`
- `READY_WITH_OPEN_WORK`
- `BLOCKED_INTEGRITY`
- `BLOCKED_MISSING_AUTHORITY`
- `HISTORICAL_ONLY`

This release is `READY_WITH_OPEN_WORK` because Epic 01–12 are complete while `BL-BENCH-041` remains open.

## Canonical outputs

- `HANDOFF_POLICY.yaml`
- `handoff/HANDOFF_README.md`
- `handoff/CURRENT_STATE.md`
- `handoff/NEXT_ACTION.md`
- `handoff/TRANSFER_PROMPT.md`
- `templates/HANDOFF_MANIFEST.template.yaml`
- `schemas/handoff_manifest.schema.json`

## Completion criteria

`BL-BENCH-040` is complete when the handoff contract, receiver preflight, manifest, reading order, transfer prompt and integrity evidence exist and pass self-validation.
