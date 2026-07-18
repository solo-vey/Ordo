# A7 — Regression Validation, Final Package Assembly and Release-Candidate Closure

## Status

`release-candidate-ready-for-human-confirmation`

## Release identity

- Module: `ordo.applied_project_factory`
- Previous confirmed baseline: `v0.1.0-rc.12-confirmed-closure`
- Candidate version: `v0.1.0-rc.13-ordo-v0.12-adaptation-release-candidate`
- Language target: `Ordo v0.12 pre-release`
- Adaptation milestones included: `A0`–`A7`

## Regression conclusion

The Ordo v0.12 adaptation preserves the confirmed APF responsibility boundary and authoring methodology. The adaptation adds explicit program-level metadata, interaction/process-rail contracts, Prompt Registry conventions, source/IR/state/checkpoint contracts, validation/release-hygiene rules and a real capability audit. It does not execute a real playbook intake, create a concrete domain playbook, modify Ordo core, or start deferred backlog implementation.

## Capability boundaries retained

- Runtime-supported: checkpoint state, forward blocking, snapshots/hash chain, session trace/verification, append-only restore-session.
- Helper-supported: state diff.
- Package-local: generalized prompt application trace evidence.
- Policy-only: semantic downstream stale-dependency invalidation.
- Pilot-only: transcript replay protocol.
- Blocked: multi-runtime transcript replay acceptance.

## Release gates

- A0–A6 artifacts present: passed.
- Program contract and metadata aligned: passed.
- Interaction model/process rail/conversation semantics aligned: passed.
- Prompt Registry integrity and prompt checksums: passed.
- Source → IR → state → outputs contract aligned: passed.
- Validation profile and package-class hygiene aligned: passed.
- JSON syntax validation: passed.
- YAML syntax validation: passed.
- Whole-package checksum regeneration: passed.
- ZIP integrity: passed after assembly.
- Deferred backlog untouched: passed.
- Human confirmation: pending.

## Closure decision

A7 closes the technical adaptation line as a release candidate. It does **not** convert the candidate into a confirmed baseline automatically. The previous confirmed baseline remains authoritative until explicit human confirmation of this package.


## Post-candidate confirmation

This historical release-candidate artifact was accepted by the process owner on 2026-07-10. The active confirmed baseline is `v0.1.0-rc.13-ordo-v0.12-adaptation-confirmed-closure`. See `docs/APF_RC13_CONFIRMED_CLOSURE_ACCEPTED_BASELINE.md`.
