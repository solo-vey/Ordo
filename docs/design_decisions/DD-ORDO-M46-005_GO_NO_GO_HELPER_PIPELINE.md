# DD-ORDO-M46-005 — Go/No-Go helper pipeline

## Status

Accepted for M46.5.

## Context

After M46.2–M46.4, Ordo can validate contract/artifact mappings, rendered artifacts and cross-artifact consistency. A reviewer still needed to run several commands and manually interpret whether the package was ready.

## Decision

Add `ordo go-no-go` as a deterministic helper command that composes the release/readiness checks into one machine-readable decision.

The command writes `reports/GO_NO_GO_REPORT.json` and returns exit code `0` only when the status is `go`.

## Pipeline

```text
lint → compile → coverage → validate-state → validate-artifacts → consistency → go/no-go
```

Optional switches allow running guided intake and output generation first:

```bash
ordo go-no-go <package> --run-intake --answers <answers.yaml> --generate-output
```

## Non-goals

- No AI model execution.
- No live REST/Mongo/queue execution.
- No replacement for project-specific runtime/business tests.

## Consequence

A pre-release reviewer can now use one command to determine whether confirmed contracts reached generated artifacts consistently.
