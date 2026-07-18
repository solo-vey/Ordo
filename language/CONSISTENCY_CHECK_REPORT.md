# Consistency Check Report

`CONSISTENCY_CHECK_REPORT.json` is the machine-readable report that compares generated artifacts against confirmed contracts and against each other.

It belongs after rendered artifact validation:

```text
confirmed contracts
→ artifact requirements
→ rendered artifacts
→ validate-artifacts
→ consistency report
```

## Minimum shape

```json
{
  "status": "passed | failed | passed_with_warnings",
  "mode": "cross_artifact_consistency",
  "go_no_go": "go | no_go_requires_artifact_fix",
  "checked_contracts": [],
  "checked_artifacts": [],
  "blocking_issues": [],
  "warnings": [],
  "cross_artifact_consistency": {}
}
```

## Failure examples

- `ORDO-COV-002` — a confirmed contract field is missing from required artifacts.
- `ORDO-COV-004` — generated artifacts disagree on the same confirmed contract field.

## Boundary

The report is deterministic. It checks declared contract fields and rendered artifact content. It does not judge business correctness beyond the declared contracts.
