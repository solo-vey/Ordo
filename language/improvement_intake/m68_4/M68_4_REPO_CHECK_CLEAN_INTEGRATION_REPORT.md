# M68.4 — Repo-check Clean Integration Report

Status: `implemented-optional-integration / passed-cli-validation`

## Scope

M68.4 adds optional `repo-check --clean` integration after M68.3 design acceptance.

## Implemented

- Added repo hygiene aggregation in `cli/ordo/repo_checks.py`.
- Added `repo-check --clean` CLI flags in `cli/ordo/cli.py`.
- Added `cli/tests/test_repo_check_clean_integration.py`.
- Added `cli/docs/REPO_CHECK_CLEAN_INTEGRATION.md`.
- Updated repo hygiene and clean-check docs.

## Command

```bash
ordo repo-check <repo> --clean
ordo repo-check <repo> --clean --profile light|standard|strict
ordo repo-check <repo> --clean --fail-on-warning
ordo repo-check <repo> --clean --json
```

## Policy

The integration reads an explicit repo hygiene policy from the repo root. Without policy, it does not wide-enforce applied packages and reports discovered package roots as delegated.

## Validation

Targeted tests passed:

```bash
PYTHONPATH=cli python -m unittest cli.tests.test_clean_check_fixtures cli.tests.test_repo_check_clean_integration -v
```

Result: `Ran 15 tests / OK`.

## Non-goals

No runtime regeneration, lockfile regeneration, embedded CLI rebuild, compiler changes, runtime core changes, opcode changes, or applied package edits.
