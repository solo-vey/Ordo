# M68 First-Wave Closure Report

## Closure line

`M68.0 → M68.1 → M68.2 → M68.3 → M68.4`

## Status

`closed-first-wave / passed`

## Scope

M68 closes the first hardening wave for `ordo clean-check` and its optional repo-level aggregation through `repo-check --clean`.

This closure is limited to the Ordo language / CLI / utility layer. It does not apply standards to concrete applied packages and does not mutate package-local `program.ordo.yaml` files.

## Accepted milestones

### M68.0 — CLI clean-check hardening plan + fixture matrix

Accepted as planning/design. It defined the hardening sequence, fixture matrix, repo-level hygiene direction, and the split between package-level `clean-check` and repo-level aggregation.

### M68.1 — real fixture test suite for clean-check

Accepted as test-suite implementation. It added real fixture packages under `cli/tests/fixtures/clean_check/` and targeted tests for clean, broken, warning, manifest, startup, prompt, derived-artifact, JSON, `--out`, and `--fail-on-warning` behavior.

### M68.2 — clean-check output / exit-code hardening

Accepted as CLI hardening. It stabilized report shape, schema version, profile reporting, summary counters, and exit-code policy.

### M68.3 — repo-level package hygiene design

Accepted as design. It established `repo-check --clean` as the correct future direction, keeping `clean-check` package-level and repo-check as read-only aggregation/policy layer.

### M68.4 — optional repo-check integration

Accepted as optional implementation. It added `repo-check --clean` with explicit policy-based enforcement and default delegation behavior for applied packages.

## Final accepted behavior

Package-level check:

```bash
ordo clean-check <package>
ordo clean-check <package> --profile light|standard|strict
ordo clean-check <package> --json
ordo clean-check <package> --fail-on-warning
ordo clean-check <package> --out <path>
```

Repo-level optional aggregation:

```bash
ordo repo-check <repo> --clean
ordo repo-check <repo> --clean --profile light|standard|strict
ordo repo-check <repo> --clean --fail-on-warning
ordo repo-check <repo> --clean --json
ordo repo-check <repo> --clean --out <path>
```

Without explicit `repo_hygiene.yml`, repo-level clean mode remains non-invasive and reports package roots as delegated/not-applicable rather than enforcing checks across applied packages.

## Validation summary

- M68.0 validation: passed
- M68.1 validation: passed
- M68.2 validation: passed
- M68.3 validation: passed
- M68.4 validation: passed
- Targeted CLI tests: passed
- JSON report parsing: passed
- Scope guards: passed
- Zip integrity: passed

Targeted command:

```bash
PYTHONPATH=cli python -m unittest cli.tests.test_clean_check_fixtures cli.tests.test_repo_check_clean_integration -v
```

Result: `Ran 15 tests / OK`.

## Non-changes

M68 first wave did not change:

- applied package source files;
- package-local `program.ordo.yaml` files;
- runtime core;
- compiler behavior;
- opcodes;
- compiled IR artifacts;
- lockfiles;
- embedded CLI bundles.

## Next backlog candidates

- M69 — repo hygiene policy fixtures and strict-mode scenarios;
- M69 — release-gate profile for stable package index;
- M69 — clean-check documentation examples with safe synthetic packages;
- future — optional CI recipe for `ordo clean-check` and `ordo repo-check --clean`.
