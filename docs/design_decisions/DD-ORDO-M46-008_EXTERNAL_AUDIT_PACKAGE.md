# DD-ORDO-M46-008: External Audit Package for Pre-release Candidate

## Status

Accepted for M46.8.

## Context

M46.1–M46.7 added the contract/artifact coverage model, rendered artifact validation, consistency checks, go/no-go pipeline, and pre-release source-archive hygiene. Before treating the package as a pre-release candidate, Ordo needs a repeatable external audit route.

## Decision

Add a reviewer-facing external audit prompt and checklist. These files define how an independent reviewer or fresh AI session should inspect the archive, run CLI checks, verify active packages, validate generated artifacts, and issue a go/no-go style audit verdict.

## Consequences

- External review is no longer an ad hoc conversation.
- Validation reports remain useful but are not treated as sufficient proof.
- The package can be handed to another model/person with a concrete audit script.
- No CLI behavior or language semantics are changed in this milestone.

