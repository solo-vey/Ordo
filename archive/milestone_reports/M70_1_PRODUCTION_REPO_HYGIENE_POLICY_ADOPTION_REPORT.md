# M70.1 — Production `repo_hygiene.yml` Adoption Report

Status: `implemented-safe-initial-policy / passed-validation`

## Result

A production root `repo_hygiene.yml` is now present. It adopts the M70.0 Phase A classification without falsely claiming package-level enforcement for `language/` or `cli/`.

## Effective policy

- `language/`: `not_applicable`, release-critical, dedicated root contract pending.
- `cli/`: `not_applicable`, release-critical, dedicated root contract pending.
- `cli/examples/history_event_guided_intake/`: `optional`, actually clean-checked.
- `packages/`: `delegated`; package children are not centrally enforced.
- `utilities/`, `ordo_pathwalk/`, `book/`, `docs/`: `not_applicable`.
- `.github/`, `reports/`: `ignored` by package clean-check.
- no root is marked `required`.

## Production smoke result

`ordo repo-check . --clean --profile standard` returned `passed` with one checked optional root, one delegated root and eight not-applicable/ignored roots.

## Scope

No changes were made to applied packages, CLI implementation, runtime, compiler, opcodes, compiled IR, lockfiles or embedded CLI bundles.
