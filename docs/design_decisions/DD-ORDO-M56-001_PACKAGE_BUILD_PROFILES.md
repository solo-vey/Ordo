# DD-ORDO-M56-001 — Package build profiles

## Decision

Ordo subject packages now support three explicit build profiles:

- `dev` — full editable source package.
- `runtime` — clean executable package based on compiled IR.
- `evidence` — validation/provenance/hash reports only.

## Reason

Runtime guided intake should not be forced to carry source YAML, tests, run inputs, generated outputs, snapshots, release archives, and debug notes. Those files are useful during development but can confuse runtime execution. The runtime package must use `compiled/program.ir.json` as the primary runtime source.

## Consequences

`ordo package` now supports `--profile dev|runtime|evidence`. Runtime builds generate `ordo.runtime.json`, `reports/BUILD_MANIFEST.json`, and `reports/SHA256SUMS.txt`, and fail on missing/stale compiled IR or misleading CLI evidence.
