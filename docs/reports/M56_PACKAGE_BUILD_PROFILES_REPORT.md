# M56 Package Build Profiles Report

## Scope

M56 adds package build profiles to the Ordo Developer Bundle:

```text
dev / runtime / evidence
```

## Main changes

- Added `cli/ordo/package_profiles.py`.
- Added `ordo package --profile dev|runtime|evidence`.
- Added `ordo.runtime.json` generation for runtime packages.
- Added `reports/BUILD_MANIFEST.json` and `reports/SHA256SUMS.txt` generation.
- Added package-profile validation errors `ORDO-PACKAGE-001` … `ORDO-PACKAGE-010`.
- Updated package template and active subject packages with `PACKAGING_PROFILES.md`.
- Added regression tests for profile contents, stale/missing IR, and false CLI-passed claims.

## Validation

Final validation is recorded in root `M56_VALIDATION_REPORT.json`.
