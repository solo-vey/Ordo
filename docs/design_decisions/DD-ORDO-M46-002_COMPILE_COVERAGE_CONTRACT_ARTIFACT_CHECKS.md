# DD-ORDO-M46-002 — Compile/Coverage checks for contract → artifact references

## Status

Accepted for M46.2.

## Context

M46.1 introduced first-class language concepts for `contract`, `artifact_requirement`, `coverage_rule`, `rendered_artifact_assertion` and `go_no_go`.

The next pre-release requirement is not full rendered artifact validation yet. The immediate need is a deterministic source-level check that prevents a package from declaring confirmed contracts without a route to generated artifacts.

## Decision

M46.2 adds a narrow helper module in CLI:

```text
cli/ordo/contract_coverage.py
```

and wires it into:

```text
ordo compile
ordo coverage
```

`compile` validates references and schema-level source consistency.

`coverage` validates confirmed contract mapping coverage.

## Non-goals

M46.2 does not validate rendered Markdown/JSON/YAML content. That remains a separate M46 step.

## Consequences

A package can now fail before generated artifacts are inspected if it has invalid contract/artifact references or no declared mapping for confirmed contracts.
