# APF RC Standard Module Status — M63.1

Status: `release-candidate / go`  
Module id: `ordo.applied_project_factory`  
Version: `0.1.0-rc.1`  
Lifecycle: `release-candidate`  
Standard applied module: `true`  
Parent language line: `Ordo v0.12 / M62 line closure`  
Generated: `2026-07-08T17:14:37.838821+00:00`

## Decision

APF `v0.1.0-rc.1` is accepted for package-level release-candidate import into the current Ordo language package line as a **standard applied module**.

This import replaces the historical M62 import point `0.1.0-alpha.14` as the current APF package. Alpha.14 remains a historical milestone only.

## Validation profile

Required parent-compatible checks:

| Check | Status |
|---|---|
| lint | passed |
| compile | passed |
| test | passed |
| coverage | passed |
| validate-state | passed |
| next-step | generated |
| validate-output | passed |
| validate-artifacts | passed |
| consistency | passed_with_warnings |
| go/no-go | go |
| repo-check clean source | passed |

Optional / APF-local:

- `validate-factory-output` remains APF-local or optional until promoted to parent CLI. Its absence in the parent CLI is not a blocker when equivalent APF-local reports are present.

## Known limitations

- `FLOW.JOIN` remains a future IR candidate.
- `SHARED.TAIL.REFERENCE` remains a future IR candidate.
- `validate-factory-output` remains APF-local / optional.
- `consistency: passed_with_warnings` remains visible and non-blocking.

## Core/runtime boundary

This import does not promote APF workflow concepts into required core runtime opcodes. APF remains a standard applied module with concrete workflow logic, package-authoring flow, human review flow, output/template review, validation and handoff tail.
