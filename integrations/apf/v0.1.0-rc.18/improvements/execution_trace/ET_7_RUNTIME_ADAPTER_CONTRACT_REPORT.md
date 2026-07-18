# ET-7 — Runtime adapter contract

Status: `completed`

APF now defines the runtime adapter boundary required when a generated playbook uses `runtime_mode: runtime_enforced`.

## Added

- `docs/APF_EXECUTION_TRACE_RUNTIME_ADAPTER_CONTRACT.yaml`
- `templates/GENERATED_PLAYBOOK_TRACE_ADAPTER_CONTRACT.template.yaml`
- `templates/GENERATED_PLAYBOOK_TRACE_ADAPTER_CONFORMANCE_REPORT.template.yaml`

## Contract boundary

APF generates configuration, schema, event mapping, security, replay and adapter contracts. The target runtime adapter creates and persists actual `EXECUTION_TRACE` artifacts.

## Required operations

Initialize, append, state reference, pause/resume, finalize/fail/cancel, integrity, store/load, replay preparation and capture toggle.

## Blocking rules

The adapter must preserve append-only semantics, monotonic sequence, redaction-before-persistence, terminal lifecycle completeness, idempotency, and fail-closed behavior for required events.

APF internal tracing remains disabled by default.
