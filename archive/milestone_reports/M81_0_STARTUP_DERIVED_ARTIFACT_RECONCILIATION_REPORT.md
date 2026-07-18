# M81.0 Startup / Derived Artifact Reconciliation Report

Status: `passed` for `packages/history_event_guided_intake`.

## Result

- startup profile present and default mode resolves;
- declared startup entries exist;
- strict `artifact_sync` added to the real package;
- five derived artifacts are declared with SHA-256 fingerprints;
- reconciliation tests pass.

## Remaining blocker

The repository-level strict clean gate still blocks because generated APF artifacts are present in the source workspace:

- `packages/ordo_applied_project_factory/compiled/program.ir.json`
- `packages/ordo_applied_project_factory/compiled/program.ordo.view`
- `packages/ordo_applied_project_factory/compiled/targets.manifest.json`
- `packages/ordo_applied_project_factory/reports/compile_report.json`
- `packages/ordo_applied_project_factory/reports/lint_report.json`
- `packages/ordo_applied_project_factory/runtime/session.ordo.trace`

These must be removed from the source package or moved into an explicitly delegated/generated workspace before BL-ORDO-012 can be closed.
