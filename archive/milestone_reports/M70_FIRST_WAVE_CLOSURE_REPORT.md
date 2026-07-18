# M70 First-Wave Closure Report

## Status

`closed-first-wave / passed-validation`

## Closed line

- M70.0 — production repo hygiene policy design and root classification
- M70.1 — safe initial `repo_hygiene.yml` adoption
- M70.2 — language/CLI root contract design and repo-check integration
- M70.3 — not required: M70.2 production smoke found no hygiene blockers requiring remediation
- M70.4 — production CI/release validation

## Consolidated outcome

The repository now has an explicit production hygiene policy. `language/` and `cli/` are enforced as release-blocking non-package root contracts without synthetic `ordo.yml` manifests. Applied packages remain delegated. PR, main, and release workflows continue to call the existing `ordo repo-check --clean` CLI path.

## Validation

- prior M70.4 targeted regression: 46 tests, OK
- closure bounded regression: 12 tests, OK
- workflow YAML parsing: passed
- production policy parsing: passed
- standard and strict production smokes: passed
- language root contract: passed
- CLI root contract: passed
- packages delegation: confirmed
- scope guards: passed
- archive integrity: passed

A single consolidated test invocation hit the execution time limit during a known slow smoke test after 33 preceding tests had passed. The remaining M70-specific suites were then executed separately and all 12 tests passed. The accepted M70.4 evidence already records the complete 46-test successful run.

## Untouched scope

- `packages/*`
- runtime core
- compiler behavior
- opcodes
- compiled IR
- lockfiles
- embedded CLI bundles
