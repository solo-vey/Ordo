# M46.3 — validate-artifacts

## Purpose

`ordo validate-artifacts` checks rendered Markdown/JSON/YAML files after output generation.

It is intentionally different from `compile` and `coverage`:

```text
compile            checks source references
coverage           checks contract → artifact mapping
validate-artifacts checks rendered file content
```

## Command

```bash
ordo validate-artifacts <package>
ordo validate-artifacts <package> --artifacts <generated-artifacts-dir>
ordo validate-artifacts <package> --state <run-state.yaml>
```

Default paths:

```text
artifacts: <package>/generated_outputs
state: latest reports/intake_report.json or reports/run_report.json
report: <package>/reports/artifact_validation_report.json
```

## What it checks in M46.3

- required rendered artifact files exist;
- confirmed contract field values appear in required artifacts;
- rendered artifact assertions are satisfied;
- candidate/proposed values are not silently rendered as confirmed values.

## Error examples

```text
ORDO-COV-002 Confirmed contract field value is missing from required artifact.
ORDO-COV-003 Artifact contains a candidate/proposed contract value as if it were confirmed.
ORDO-COV-012 Generated artifacts directory does not exist.
```

## Current limitation

M46.3 performs deterministic token/value presence checks. It does not yet provide full cross-artifact semantic contradiction detection; that belongs to the next `consistency` slice.
