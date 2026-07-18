# 06. Debug, Test & Improvement Layer

## Purpose

Цей шар робить Ordo-програми пояснюваними, перевірюваними і керовано покращуваними.

```text
execute → trace → explain → test → capture feedback → suggest patch → approve → regress
```

## Trace source

Кожен execution trace MUST мати:

```yaml
trace_source: model_self_report | runtime_enforced | hybrid
```

### Meaning

- `model_self_report` — модель сформувала пояснення. Це корисно, але не є runtime-доказом.
- `runtime_enforced` — trace сформовано кодом runner-а на основі реальних переходів.
- `hybrid` — механічні частини зафіксовані runtime-ом, семантичні пояснення — модельні.

## Canonical execution trace

New programs use the first-class `execution_trace:` element defined by `33_EXECUTION_TRACE_MODEL.md`. The older `trace:` shape below is retained as a compatibility projection.

## Required legacy trace sections

```yaml
trace:
  run_id: RUN-001
  execution_mode: chat_internal
  trace_source: hybrid
  selected_path: {}
  rejected_paths: []
  decision_log: []
  state_snapshots: []
  state_diffs: []
  gate_report: []
  knowledge_trace: []
  warnings: []
  violations: []
```

## Improvement records

User feedback має перетворюватись на structured record:

```yaml
improvement_record:
  id: IR-001
  type: missed_required_gate
  severity: high
  affected_unit:
    id: domain_pack.history_event.G_PACKAGE_SELF_CHECK
    kind: gate
  root_cause_hypothesis: []
  proposed_patch: []
  suggested_tests: []
  approval:
    required: true
    status: pending
```

## New feedback class

```text
node_coverage_gap
```

Виникає, коли користувацький input не потрапляє в `allowed_answers` і активується `on_unmatched_input`.
