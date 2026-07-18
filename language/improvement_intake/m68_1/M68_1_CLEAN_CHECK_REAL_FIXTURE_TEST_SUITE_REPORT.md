# M68.1 — CLI clean-check real fixture test suite

Status: implemented-fixture-tests / passed-cli-fixture-validation

## Scope

M68.1 adds real clean-check fixture packages and a targeted CLI/API test suite for
`ordo clean-check`.

## Added

- `cli/tests/fixtures/clean_check/*`
- `cli/tests/test_clean_check_fixtures.py`

## Changed

- `cli/docs/CLEAN_CHECK_FIXTURE_MATRIX.md`
- `cli/docs/CLEAN_CHECK_COMMAND.md`
- root and language index/report files

## Explicit non-changes

- No applied package changes.
- No `packages/` changes.
- No CLI implementation changes in `cli/ordo/*.py`.
- No runtime core changes.
- No compiler changes.
- No opcodes added.
- No compiled IR regeneration.
- No lockfile regeneration.

## Validation

- Targeted fixture tests pass.
- JSON reports parse.
- Scope guards pass.
- Zip integrity passes.
