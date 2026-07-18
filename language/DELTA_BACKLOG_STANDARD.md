# Delta Backlog Standard

Status: M67.0 accepted draft standard.

Delta backlog records known package deltas that are intentionally deferred. They are explicit follow-up items, not hidden warnings in prose.

## When required

A delta backlog entry is required when a package change intentionally leaves a derived artifact, validation profile, prompt registry, startup profile, manifest, graph export, report, or documentation section out of sync.

## Canonical block

```yaml
delta_backlog:
  backlog_id: history_event_factory_delta_backlog
  policy: explicit_deferred_deltas_only
  entries:
    - delta_id: D-M67-001
      title: Regenerate compiled runtime IR after source updates
      area: compiled_ir_regeneration
      severity: warning
      source_change:
        - packages/history_event_guided_intake/source/program.ordo.yaml
      affected_artifacts:
        - packages/history_event_guided_intake/ordo.runtime.json
      reason_deferred: Runtime compilation is outside this package-consistency milestone.
      required_resolution: Regenerate compiled runtime IR in a later runtime gate.
      release_blocking: false
```

## Severity

- `error`: must be resolved before release/acceptance.
- `warning`: allowed only if recorded and justified.
- `info`: informational.

## Non-goals

No issue-tracker integration is prescribed by M67.0.
