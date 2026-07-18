# Chapter 69. M63: APF Release-candidate Integration

M63 opens a separate integration line for `ordo.applied_project_factory` as a release-candidate standard applied module.

Importantly, APF does not become part of runtime core. It is a standard applied module that uses Ordo to create other playbook/process packages.

## What M63.0 records

- M62 contained APF `v0.1.0-alpha.14` as a historical import point.
- The M63 target is APF `v0.1.0-rc.1`, source base `alpha.21`.
- APF patterns are classified cautiously: not all become IR/opcode.
- `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` remain future IR candidates.
- `validate-factory-output` remains APF-local or optional until stable parent-CLI semantics exist.

## Why this is a separate line

M62 closed package-level APF integration as a standard module. M63 must perform release-candidate acceptance: update the package, metadata, validation profile, known limitations, and classification matrix.

## Boundary

M63.0 does not rewrite APF YAML, change runtime core, or add new opcodes. It is a planning/delta-review gate before importing rc.1.
