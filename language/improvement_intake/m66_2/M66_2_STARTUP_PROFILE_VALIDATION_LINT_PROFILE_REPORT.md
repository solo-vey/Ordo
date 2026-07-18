# M66.2 — Startup Profile Validation / Lint Profile Design Report

**Status:** `accepted-design / passed-docs-schema-validation`

## Summary

M66.2 defines a validation/lint profile convention for `startup_package_profile`.

It adds a standard `startup_profile_validation` model with profiles, severities, readiness decisions, and check families for startup discoverability and safety.

## Added artifacts

- `language/STARTUP_PROFILE_VALIDATION_PROFILE.md`
- `language/schemas/startup_profile_validation_profile_schema.yaml`
- `language/examples/source/startup_profile_validation_profile_example.ordo.yaml`
- `language/spec/22_STARTUP_PROFILE_VALIDATION_MODEL.md`
- `docs/design_decisions/DD-ORDO-M66-003_STARTUP_PROFILE_VALIDATION_LINT_PROFILE.md`
- `language/improvement_intake/m66_2/M66_2_STARTUP_PROFILE_VALIDATION_LINT_PROFILE_REPORT.md`
- `language/improvement_intake/m66_2/M66_2_VALIDATION_REPORT.json`

## Updated artifacts

- `README.md`
- `CHANGELOG.md`
- `FUTURE_BACKLOG.md`
- `STABLE_PACKAGE_INDEX.md`
- `language/README.md`
- `language/CHANGELOG.md`
- `language/registry/STARTUP_PACKAGE_PROFILE_VALUES.md`

## Validation scope

- YAML schema parses.
- YAML example parses.
- JSON reports parse.
- M66.0/M66.1 artifacts remain present.
- Runtime/core/CLI/opcode files are not changed.

## Non-change statement

No runtime-core changes, compiler changes, CLI changes, opcodes, or compiled IR regeneration are included in M66.2.
