# M66.0 — Package Startup Standard / Startup Package Profile Report

## Status

`accepted-docs-schema-convention / passed-validation`

## Summary

M66.0 adds the Package Startup Standard and `startup_package_profile` convention.

This milestone standardizes how Ordo packages declare:

- startup modes;
- entry files;
- default startup path;
- role/audience-specific startup surfaces;
- readiness gates;
- startup authority boundaries.

## Added files

- `language/PACKAGE_STARTUP_STANDARD.md`
- `language/STARTUP_PACKAGE_PROFILE.md`
- `language/registry/STARTUP_PACKAGE_PROFILE_VALUES.md`
- `language/schemas/startup_package_profile_schema.yaml`
- `language/examples/source/startup_package_profile_example.ordo.yaml`
- `language/spec/21_PACKAGE_STARTUP_MODEL.md`
- `docs/design_decisions/DD-ORDO-M66-001_PACKAGE_STARTUP_STANDARD.md`
- `language/improvement_intake/m66_0/M66_0_VALIDATION_REPORT.json`

## Updated files

- `README.md`
- `CHANGELOG.md`
- `FUTURE_BACKLOG.md`
- `STABLE_PACKAGE_INDEX.md`
- `language/README.md`
- `language/CHANGELOG.md`
- `language/VALIDATION_REPORT.json`

## Explicit non-changes

- runtime core unchanged;
- compiler behavior unchanged;
- CLI commands unchanged;
- opcodes unchanged;
- History Event Factory runtime logic unchanged;
- APF package logic unchanged;
- compiled IR not regenerated.

## Acceptance criteria

- startup package profile convention documented;
- schema convention added;
- example source parses as YAML;
- registry values documented;
- spec chapter added;
- validation report added;
- startup authority boundary documented.

## Next recommended milestone

M66.1 may apply `startup_package_profile` to `packages/history_event_guided_intake/` as a package-local startup profile patch.
