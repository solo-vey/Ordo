# M67.3 — CLI Clean-Check Minimal Implementation Patch Report

Status: `implemented-minimal / passed-cli-validation`

## Scope

M67.3 implements the minimal `ordo clean-check` CLI command defined by M67.2.

This is a CLI / utility-level patch only. It does not modify applied package source YAML, package prompts, package startup profiles, runtime core, compiler behavior, Semantic JSON IR, opcodes, compiled artifacts, lockfiles, or embedded CLI bundles.

## Implemented command

```bash
ordo clean-check <package>
ordo clean-check <package> --profile light|standard|strict
ordo clean-check <package> --json
ordo clean-check <package> --fail-on-warning
ordo clean-check <package> --out reports/clean_check_report.json
```

## Added files

- `cli/ordo/clean_check.py`
- `M67_3_CLI_CLEAN_CHECK_IMPLEMENTATION_REPORT.md`
- `M67_3_CLI_CLEAN_CHECK_IMPLEMENTATION_REPORT.json`
- `M67_3_VALIDATION_REPORT.json`
- `language/improvement_intake/m67_3/M67_3_CLI_CLEAN_CHECK_IMPLEMENTATION_REPORT.md`
- `language/improvement_intake/m67_3/M67_3_CLI_CLEAN_CHECK_IMPLEMENTATION_REPORT.json`
- `language/improvement_intake/m67_3/M67_3_VALIDATION_REPORT.json`

## Changed files

- `cli/ordo/cli.py`
- `cli/tests/test_cli_workflow.py`
- `cli/docs/CLEAN_CHECK_COMMAND.md`
- `README.md`
- `CHANGELOG.md`
- `STABLE_PACKAGE_INDEX.md`
- `language/VALIDATION_REPORT.json`

## Minimal v1 checks

- `package_root_exists`
- `package_manifest_present`
- `package_manifest_parse`
- `source_yaml_declared`
- `source_yaml_exists`
- `source_yaml_parse`
- `declared_manifest_paths_exist`
- `declared_manifest_checksums_match`
- `prompt_registry_refs_resolve_when_present`
- `startup_profile_entries_exist_when_present`
- `derived_artifacts_current_or_backlogged_when_declared`
- `delta_backlog_blockers_not_expired_when_declared`

## Output contract

The command writes `reports/clean_check_report.json` by default and optionally prints deterministic JSON with `--json`.

Statuses are:

- `passed`
- `passed_with_warnings`
- `blocked`
- `not_applicable`

## Boundary guard

M67.3 does not change:

- `packages/*`
- package-local `program.ordo.yaml`
- runtime core
- compiler behavior
- opcodes
- compiled IR
- lockfiles
- embedded CLI bundles

## Validation summary

- Python syntax compile for `cli/ordo/clean_check.py` and `cli/ordo/cli.py`: passed
- targeted clean-check tests: passed
- command help includes `clean-check`: passed
- diff guard for `packages/`: passed
- zip integrity: passed
