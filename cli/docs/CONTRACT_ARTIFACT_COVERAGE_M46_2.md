# M46.2 — Contract → Artifact coverage checks

## Purpose

M46.2 adds the first deterministic layer for checking whether confirmed process contracts have declared artifact coverage.

This is intentionally narrower than rendered artifact validation:

```text
compile      → checks contract/artifact references in source
coverage     → checks confirmed contract → artifact requirement mapping
future step  → checks rendered Markdown/JSON/YAML artifact content
```

## Compile-time checks

`ordo compile` now fails when:

- an `artifact_requirement` references an unknown contract;
- an `artifact_requirement` references an unknown artifact;
- an `artifact_requirement` references an unknown contract field;
- a `rendered_artifact_assertion` references an unknown contract, field or artifact;
- contract or artifact status/shape is invalid.

The result is written to:

```text
reports/compile_report.json
```

under:

```json
"contract_artifact_reference_check": { ... }
```

## Coverage checks

`ordo coverage` now includes:

```json
"contract_artifact_coverage": { ... }
```

It fails when a confirmed contract has no artifact mapping, or when a confirmed required contract field has no mapping.

## Current limitation

M46.2 does not inspect rendered files. It validates declared model coverage only. Rendered artifact validation is planned for the next M46 step.
