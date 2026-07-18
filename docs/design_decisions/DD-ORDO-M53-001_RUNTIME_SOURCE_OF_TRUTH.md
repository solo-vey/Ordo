# DD-ORDO-M53-001 — Runtime Source-of-Truth / Stale IR / CLI Truthfulness

## Status

Accepted for v0.12 preview candidate.

## Decision

Ordo Developer workflows must treat a package as a runtime chain, not as unrelated files:

```text
ordo.yml → source/program.ordo.yaml → compiled/program.ir.json → run_state → generated_outputs
```

Helper commands that guide execution (`validate-state`, `check-gate`, `next-step`) must require current compiled IR. If the editable source is newer than the IR, the helper must block with `ORDO-RUNTIME-004`.

Generated outputs must not be produced before a successful `validate-state`, and package archives must not be produced before successful `validate-output` unless an explicit override is used.

Reports must declare CLI truthfulness using explicit statuses such as `executed_cli_passed` or `logical_self_check_only`.

## Rationale

The AI Ordo Developer should not guide a process from memory when a deterministic runtime is available. Stale IR and false validation claims are release-quality risks.

## Consequences

- New command: `ordo runtime-status`.
- New command: `ordo validate-cli-status`.
- New runtime errors: `ORDO-RUNTIME-001` through `ORDO-RUNTIME-006`.
- Stricter output order: `ORDO-COV-005` and `ORDO-COV-006`.
