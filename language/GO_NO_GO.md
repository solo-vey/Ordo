# Go/No-Go Decision

`go_no_go` is the final machine-readable decision object for a package draft or release candidate.

It summarizes deterministic checks from lint, compile, coverage, state validation, rendered artifact validation, and consistency.

## Statuses

```text
go
no_go_requires_confirmation
no_go_requires_artifact_fix
no_go_requires_template_fix
no_go_requires_runner_contract
```

## Minimal shape

```json
{
  "kind": "go_no_go",
  "status": "go",
  "blocking_issues": [],
  "warnings": []
}
```

The user-facing assistant may summarize this object, but the raw object remains the source of truth.
