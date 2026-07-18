# DD-ORDO-M67-001 — Derived Artifact Sync / Delta Backlog / Prompt Registry Packaging Checks

Status: Accepted in M67.0.

## Decision

Introduce a package-consistency design layer for derived artifact sync declarations, structured delta backlog entries, and prompt/startup packaging checks.

## Reason

M65 and M66 added prompt registry and startup profile surfaces. These surfaces increase package usefulness but also increase drift risk. M67.0 makes this drift reviewable.

## Accepted scope

Documentation, schemas, examples, registry values, and validation-profile semantics.

## Rejected scope

CLI tooling, automatic artifact regeneration, compiler hooks, runtime hooks, and new IR semantics.

## Consequence

Future packages can be reviewed against a clearer consistency contract. Tooling can later implement these checks without changing the conceptual model.
