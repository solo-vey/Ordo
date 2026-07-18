# M60.5.2b — PathWalk External Job Dry-run Contract

## Scope

This patch introduces an external-job execution contract for PathWalk dry-run benchmarks. It does not change Ordo runtime core semantics.

## Added commands

- `ordo-pathwalk dry-run-plan`
- `ordo-pathwalk dry-run-job`
- `ordo-pathwalk dry-run-collect`

## Rationale

The previous multi-case parent runner could still hang in constrained environments. The new contract decomposes a dry-run into independent jobs that can be executed by shell/CI/supervisor tooling and then collected.

## Acceptance

- Plan creation produces `DRY_RUN_PLAN.json`.
- Independent job invocation produces one score file per scenario/runtime_view.
- Collect produces `RAW_METRICS.csv`, `SUMMARY.json`, and `SUMMARY.md`.
- Regression test covers plan → job → collect.
