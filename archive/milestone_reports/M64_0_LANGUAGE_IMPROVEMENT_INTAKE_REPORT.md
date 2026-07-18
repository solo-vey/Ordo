# M64.0 Language Improvement Intake Report

Status: `passed-intake-classification`
Generated: `2026-07-09T18:40:00+02:00`

## Scope

M64.0 accepts `ORDO_LANGUAGE_IMPROVEMENT_INTEGRATION_PACK_M64_PREP` as an official planning/intake artifact for the Ordo language package.

This milestone is intentionally **classification-only**:

```text
no runtime-core changes
no compiler changes
no CLI command changes
no new opcodes
no FLOW.JOIN implementation
no SHARED.TAIL.REFERENCE implementation
no runtime execution/scoring/calibration
```

## Intake result

The uploaded pack is preserved under:

```text
docs/improvement_intake/M64_PREP_PACK/
```

The pack validates itself as `passed` and contains no blockers. Its own notes correctly state that it is a planning package, not a compiled runtime release.

## Main accepted insight

M64.0 accepts the need for a **program-level contract layer** as the next important language/package design line.

This layer covers:

```text
program metadata
interaction model
process rail policy
conversation semantics
hybrid execution boundary
program-level approval gate
startup/package profile expectations
```

## LIP classification summary

```text
total LIPs classified: 15
P0 first-wave candidates: 6
P1 later-package/documentation/tooling candidates: 6
P2 design-spike/tooling candidates: 3
runtime/opcode promotions in M64.0: 0
```

## First-wave recommendation

```text
M64.1 — Program-level contract schema convention
M64.2 — Interaction model + process rail + conversation semantics docs
M64.3 — Program-level approval gate lint/profile design
```

## Explicitly deferred

```text
FLOW.JOIN / SHARED.TAIL.REFERENCE → future IR design spike
real-module testcase runtime execution/scoring → not opened
SVG renderer implementation → companion utility only
validate-style deterministic conversation classifier → not claimed
```

## Validation summary

M64.0 validation checks are planning/doc checks only. Runtime behavior is intentionally unchanged.
