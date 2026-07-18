# M67.4 — Clean Package Gate Docs/Schema Alignment to Implemented CLI

Status: `accepted-docs-schema-alignment / passed-validation`

## Summary

M67.4 aligns the language-level clean package gate documentation and schema conventions with the implemented M67.3 `ordo clean-check` CLI command.

## Added

- `language/CLEAN_PACKAGE_GATE.md`
- `language/DERIVED_ARTIFACT_SYNC_VALIDATION_PROFILE.md`
- `language/schemas/clean_package_gate_schema.yaml`
- `language/schemas/derived_artifact_sync_validation_profile_schema.yaml`
- `language/examples/source/clean_package_gate_example.ordo.yaml`
- `language/spec/25_CLEAN_PACKAGE_GATE_MODEL.md`
- `docs/design_decisions/DD-ORDO-M67-004_CLEAN_PACKAGE_GATE_ALIGNMENT_TO_CLI.md`

## Changed

- `cli/docs/CLEAN_CHECK_COMMAND.md`
- `language/spec/24_CLEAN_PACKAGE_CLI_MODEL.md`
- root/language README and changelog/index files

## Scope boundary

No package-local files were changed. No runtime, compiler, opcode, lockfile, compiled IR, or embedded CLI behavior was changed.
