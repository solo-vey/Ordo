# BL-BENCH-054 — Execution Progress Status Output Governance

## Summary
Add a concise, evidence-bound, user-visible step progress stream during playbook execution without exposing chain-of-thought or treating chat messages as authoritative evidence.

## Status
OPEN

## Description
After each meaningful playbook step completes, render one line:

`Крок <ID> — <short observable result> — <canonical status>[: <factual reason>]`

The renderer must use a versioned status registry, bind every event to authoritative Driver/evidence records, aggregate minor sub-actions, handle correction loops and terminals, suppress unsafe or malformed events, and never alter the execution route.

## Acceptance criteria
1. Positive fixture renders canonical lines for normal, correction, plateau, blocked and terminal routes.
2. Negative fixtures suppress chain-of-thought, unsupported speculation, noncanonical status, missing evidence binding and terminal mismatch.
3. Final visible status matches the authoritative terminal record.
4. Progress events remain informational and are never accepted as proof of execution.
5. Required policy, schema, template, registry, runtime hook and test report are present.

## Evidence target
- `054_EXECUTION_PROGRESS_STATUS_OUTPUT_GOVERNANCE.md`
- `EXECUTION_PROGRESS_OUTPUT_POLICY.yaml`
- `EXECUTION_PROGRESS_STATUS_REGISTRY.yaml`
- `schemas/execution_progress_event.schema.json`
- `templates/EXECUTION_PROGRESS_EVENT.template.json`
- implementation/runtime hook
- acceptance-test report
