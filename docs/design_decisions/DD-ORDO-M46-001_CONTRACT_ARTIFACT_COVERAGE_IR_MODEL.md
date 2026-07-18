# DD-ORDO-M46-001 — Contract → Artifact Coverage IR Model

## Status

Accepted for M46.1.

## Context

Pre-release audits showed that a guided intake can confirm important contracts but fail to propagate them into all generated artifacts. This creates a false sense of readiness: the process state is rich, but Passport/Jira/Prompt/QA/JSON reports may be incomplete.

## Decision

Add first-class language and Semantic JSON IR primitives for contract-to-artifact coverage:

- `contract`
- `artifact`
- `artifact_requirement`
- `coverage_rule`
- `rendered_artifact_assertion`
- `go_no_go`

M46.1 is intentionally specification-first. It defines the model, schemas, docs, opcode catalog entries, and book source chapter, but does not yet implement full `validate-artifacts`, `consistency`, or `go-no-go` CLI behavior.

## Consequences

- Later CLI slices can implement deterministic checks without changing the conceptual model.
- Ordo packages can declare expected propagation from confirmed contracts to rendered artifacts.
- Future validation reports should be based on actual contract/artifact checks rather than manual claims.

## Non-goals

- No global rewrite of Ordo language.
- No business-logic changes to History Event packages.
- No PDF regeneration for the book in M46.1.
