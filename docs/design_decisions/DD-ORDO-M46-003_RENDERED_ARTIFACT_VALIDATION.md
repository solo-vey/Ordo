# DD-ORDO-M46-003 — Rendered Artifact Validation

## Status

Accepted for M46.3.

## Decision

Add `ordo validate-artifacts` as a deterministic helper command that validates generated Markdown/JSON/YAML artifacts against confirmed contract values.

## Context

M46.1 defined the language primitives. M46.2 made source-level contract/artifact reference and coverage checks executable. That still did not prove that rendered documents contain confirmed contract values.

## Scope

M46.3 checks:

- generated artifact directory exists;
- required artifact files exist;
- confirmed contract values appear in required artifacts;
- rendered artifact assertions pass;
- candidate/proposed values are not silently rendered as confirmed.

## Non-goals

M46.3 does not implement full semantic cross-artifact consistency. That remains for the next `consistency` slice.
