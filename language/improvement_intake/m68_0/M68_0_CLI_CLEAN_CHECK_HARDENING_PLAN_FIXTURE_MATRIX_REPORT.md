# M68.0 — CLI Clean-Check Hardening Plan + Fixture Matrix Report

Status: `accepted-plan / passed-scope-validation`

Date: 2026-07-09

## Summary

M68.0 defines the next hardening line for the implemented `ordo clean-check` command.

This milestone is planning-only. It adds the fixture matrix, exit-code expectations, JSON-output stability policy, repo-level hygiene planning notes, and follow-up implementation sequence.

## Added files

```text
cli/docs/CLEAN_CHECK_HARDENING_PLAN.md
cli/docs/CLEAN_CHECK_FIXTURE_MATRIX.md
cli/docs/REPO_LEVEL_PACKAGE_HYGIENE_PLAN.md
language/spec/26_CLI_CLEAN_CHECK_HARDENING_FIXTURE_MODEL.md
docs/design_decisions/DD-ORDO-M68-001_CLI_CLEAN_CHECK_HARDENING_PLAN_FIXTURE_MATRIX.md
M68_0_CLI_CLEAN_CHECK_HARDENING_PLAN_FIXTURE_MATRIX_REPORT.md
M68_0_CLI_CLEAN_CHECK_HARDENING_PLAN_FIXTURE_MATRIX_REPORT.json
M68_0_VALIDATION_REPORT.json
```

## Changed files

```text
README.md
CHANGELOG.md
STABLE_PACKAGE_INDEX.md
cli/docs/CLEAN_CHECK_COMMAND.md
language/README.md
language/CHANGELOG.md
language/VALIDATION_REPORT.json
```

## Explicit non-changes

```text
CLI implementation changed: no
CLI tests changed: no
packages changed: no
runtime core changed: no
compiler changed: no
opcodes added: no
compiled IR regenerated: no
lockfiles regenerated: no
embedded CLI rebuilt: no
```

## Next milestone

M68.1 — create real synthetic clean-check fixtures and tests.
