# Ordo Release Notes — ordo-2026.07.14-rc.3

## Versions

- Ordo Language: `0.13.0-rc.1` (unchanged)
- Ordo ARF/IRF: `0.2.0-rc.2`

## Completed

- BL-ORDO-035 — Test Fixture Mutation and Parallel Execution Safety.
- Negative fixture mutations must prove the fixture changed.
- `SILENT_FIXTURE_NOOP` is a blocking anti-pattern.
- Shared-workspace and wall-clock-sensitive tests execute in a quiet serial phase.

## Deferred external evidence

BL-ORDO-026 remains `ready_for_external_ci`. Its next independent full delivery gate will run only when the next version is prepared for external handoff.
