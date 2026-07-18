# M67.2 — CLI Clean-Check Support Design Report

Status: `accepted-design / passed-scope-validation`
Date: 2026-07-09

## Summary

M67.2 defines the CLI contract for a future `ordo clean-check <package>` command. It is a design milestone only and intentionally does not implement the command.

The milestone corrects the working boundary: language core, CLI design, CLI utilities, validators, and lint-profile behavior are in scope; applied package edits are out of scope.

## Added files

- `cli/docs/CLEAN_CHECK_COMMAND.md`
- `language/spec/24_CLEAN_PACKAGE_CLI_MODEL.md`
- `docs/design_decisions/DD-ORDO-M67-003_CLI_CLEAN_CHECK_COMMAND.md`
- `M67_2_CLI_CLEAN_CHECK_SUPPORT_DESIGN_REPORT.md`
- `M67_2_CLI_CLEAN_CHECK_SUPPORT_DESIGN_REPORT.json`
- `M67_2_VALIDATION_REPORT.json`

## Updated files

- `README.md`
- `CHANGELOG.md`
- `STABLE_PACKAGE_INDEX.md`
- `language/README.md`
- `language/CHANGELOG.md`
- `language/VALIDATION_REPORT.json`

## Accepted command contract

```bash
ordo clean-check <package>
ordo clean-check <package> --profile light|standard|strict
ordo clean-check <package> --json
ordo clean-check <package> --fail-on-warning
```

## Accepted status values

- `passed`
- `passed_with_warnings`
- `blocked`
- `not_applicable`

## Minimum v1 check groups

- package root and package manifest presence;
- package manifest YAML parsing;
- declared source YAML existence and parsing;
- declared manifest paths and checksum matching;
- prompt registry reference resolution when present;
- startup package profile entry-file resolution when present;
- derived artifact freshness or delta backlog coverage when declared;
- delta backlog blocker hygiene when declared.

## Explicit non-changes

M67.2 does not change:

- `packages/`;
- any package-local `program.ordo.yaml`;
- CLI implementation files under `cli/ordo/*.py`;
- CLI tests;
- runtime core;
- compiler behavior;
- opcodes;
- compiled IR;
- lockfiles;
- embedded CLI bundles.

## Next recommended milestone

M67.3 — CLI clean-check minimal implementation patch.

Before M67.3, inspect the current CLI command architecture and name the exact files to modify.
