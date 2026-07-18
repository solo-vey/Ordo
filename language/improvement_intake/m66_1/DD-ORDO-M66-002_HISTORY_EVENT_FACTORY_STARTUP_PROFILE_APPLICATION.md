# DD-ORDO-M66-002 — Apply Startup Package Profile to History Event Factory

**Milestone:** M66.1  
**Decision:** accepted

## Context

M66.0 defined `startup_package_profile` as a package/source convention. History Event Guided Intake already has Runtime Mode entry files and M65 prompt registry files. M66.1 applies the startup profile locally so the package has an explicit entry/discoverability contract.

## Decision

Add `startup_package_profile` to `packages/history_event_guided_intake/source/program.ordo.yaml` and document the package-local startup surfaces.

## Boundaries

- No runtime/core change.
- No compiler change.
- No CLI command added.
- No opcode added.
- Startup files do not override gates/state/approval/validation.
