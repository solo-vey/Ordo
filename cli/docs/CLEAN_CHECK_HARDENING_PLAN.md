# CLI Clean-Check Hardening Plan

Status: `M68.0 planning / no implementation`

This document defines the hardening plan for `ordo clean-check` after the M67.3 minimal implementation and the M67.4 clean package gate alignment.

M68.0 does not change CLI behavior. It defines the sequence, fixture matrix, expected results, and scope guards for M68.1 and later implementation milestones.

## Current baseline

The current command exists and is wired into the CLI:

```bash
ordo clean-check <package>
ordo clean-check <package> --profile light|standard|strict
ordo clean-check <package> --json
ordo clean-check <package> --fail-on-warning
ordo clean-check <package> --out <path>
```

The M67.3 implementation provides deterministic v1 checks for package root, `ordo.yml`, source YAML, optional prompt manifest checksums, prompt refs, startup profile entries, declared derived artifacts, and delta backlog blockers.

## Hardening goals

M68 hardening turns the v1 command from a minimal gate into a reliable developer/release utility.

Primary goals:

1. Preserve the existing command contract.
2. Add real fixture-based tests before widening behavior.
3. Stabilize JSON output shape and exit-code semantics.
4. Clarify `light`, `standard`, and `strict` behavior.
5. Improve diagnostics for common package hygiene failures.
6. Keep the command read-only.
7. Keep package-local applied-module changes out of this line.

## Non-goals

M68 clean-check hardening must not:

- regenerate runtime artifacts;
- regenerate lockfiles;
- rebuild embedded CLI bundles;
- mutate package source YAML;
- mutate package manifests;
- modify applied packages;
- compile package runtime artifacts;
- introduce new opcodes;
- change runtime or compiler behavior;
- claim deterministic natural-language authority review.

## Proposed M68 sequence

### M68.0 — Hardening plan and fixture matrix

Scope: docs/planning only.

Deliverables:

- hardening plan;
- fixture matrix;
- exit-code matrix;
- JSON-output stability expectations;
- repo-level hygiene planning notes;
- scope guards for follow-up milestones.

### M68.1 — Real fixture test suite

Scope: tests and test fixtures only, plus test docs.

Expected files:

```text
cli/tests/fixtures/clean_check/*
cli/tests/test_clean_check.py
```

The fixtures must be synthetic and local to the CLI test suite. They must not reuse or modify `packages/history_event_guided_intake` or any other applied package.

### M68.2 — Output and exit-code hardening

Status: `implemented` in M68.2.

Scope: CLI implementation and tests.

Expected files:

```text
cli/ordo/clean_check.py
cli/ordo/cli.py
cli/tests/test_clean_check.py
cli/docs/CLEAN_CHECK_COMMAND.md
```

Expected behavior:

- deterministic JSON key order at top-level where practical;
- stable `summary` fields;
- explicit `profile_requested` vs effective `profile` if invalid input is ever allowed outside argparse;
- predictable exit codes;
- clear separation of errors and warnings.

### M68.3 — Repo-level package hygiene design

Scope: design only unless preflight proves existing `repo-check` can be safely extended.

Candidate behavior:

- repo-level discovery of package roots;
- clean-check aggregation;
- stable package index cross-check;
- language package hygiene checks;
- no applied package mutation.

### M68.4 — Repo-check integration candidate

Scope: optional implementation only after M68.3.

Candidate command shapes:

```bash
ordo repo-check --clean
ordo clean-check . --repo
```

This is not accepted in M68.0; it remains a planned option.

## Hardening priorities

| Priority | Area | Rationale |
|---|---|---|
| P0 | fixture tests | protect existing behavior before changing implementation |
| P0 | exit-code semantics | required for CI/release gates |
| P0 | JSON output stability | required for automation and evidence files |
| P1 | profile-specific severity | required for useful authoring vs release behavior |
| P1 | better diagnostics | required for human developers to fix packages |
| P2 | repo-level aggregation | useful after package-level command is stable |
| P2 | strict waiver model | useful, but should not be invented before real failures are seen |

## Exit-code policy

| Status | `--fail-on-warning` | Exit code |
|---|---:|---:|
| `passed` | false/true | 0 |
| `passed_with_warnings` | false | 0 |
| `passed_with_warnings` | true | 1 |
| `blocked` | false/true | 1 |
| CLI usage error | n/a | argparse default |
| unexpected internal exception | n/a | non-zero; should be minimized by targeted error handling |

## JSON output stability policy

The report should continue to use this top-level shape:

```json
{
  "mode": "clean_package_check",
  "status": "passed",
  "profile": "standard",
  "package_root": "/abs/path/to/package",
  "checks": [],
  "warnings": [],
  "errors": [],
  "summary": {
    "error_count": 0,
    "warning_count": 0,
    "check_count": 0
  },
  "exit_code": 0
}
```

M68 hardening may add fields, but must not remove existing top-level fields without a design decision.

Allowed additions:

```text
profile_requested
schema_version
ordo_cli_version
started_at / generated_at
fixture_id in test evidence only
```

## Scope guards for implementation milestones

Every M68 implementation milestone must verify:

```text
packages/ unchanged
runtime core unchanged
compiler behavior unchanged
opcodes unchanged
compiled IR not regenerated
lockfiles not regenerated
embedded CLI bundles not rebuilt
```

## Open backlog after M68 first wave

The following should remain backlog unless explicitly opened:

- automatic repair/fix mode;
- runtime/lockfile regeneration;
- embedded CLI rebuild;
- deterministic natural-language prompt authority classification;
- applied-package migrations;
- repository-wide clean enforcement as a release blocker.

## M68.3 update — Repo-level package hygiene design

Status: `accepted-design / no implementation`

M68.3 defines repo-level hygiene as a future `repo-check --clean` extension rather than broadening `clean-check` into a repository command.

Accepted direction:

```bash
ordo repo-check <repo> --clean
```

Implementation remains deferred to a future M68.4 candidate after preflight. Applied packages remain delegated by default unless explicit repo policy opts them in.

## M68.4 repo-check integration status

`repo-check --clean` now acts as a repo-level aggregation layer over package-level `clean-check`. It does not replace `clean-check`, and it does not mutate package contents.
