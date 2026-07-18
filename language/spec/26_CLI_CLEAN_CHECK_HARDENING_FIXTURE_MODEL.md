# Spec 26 — CLI Clean-Check Hardening and Fixture Model

Status: `M68.0 planning`

## Purpose

This spec defines how the `ordo clean-check` command should be hardened after its minimal implementation.

The goal is to make clean package review reliable for release and handoff workflows while preserving the separation between language/CLI responsibility and applied-package ownership.

## Baseline command

```bash
ordo clean-check <package>
```

The command is a read-only consistency gate. It may report errors or warnings, but it must not repair, compile, regenerate, or mutate package files.

## Hardening model

Hardening has four layers:

1. fixture coverage;
2. output stability;
3. exit-code stability;
4. repo-level hygiene readiness.

## Fixture coverage

A fixture is a synthetic package used to test one or more clean-check outcomes.

Fixture requirements:

- local to the CLI test suite;
- deterministic;
- minimal;
- no external resources;
- no applied-package dependency;
- test expectations documented before implementation.

## Required status coverage

The fixture suite must cover:

| Status | Required? | Example source |
|---|---:|---|
| `passed` | yes | clean minimal package |
| `passed_with_warnings` | yes | light-mode checksum mismatch or expired standard blocker |
| `blocked` | yes | missing manifest, broken source, unresolved prompt ref |
| `not_applicable` | indirect | individual checks within otherwise passed reports |

## Required profile coverage

The fixture suite must cover all supported profiles:

```text
light
standard
strict
```

At least one fixture must demonstrate a difference between `light` and `standard`, and at least one fixture must demonstrate a difference between `standard` and `strict`.

## Exit-code model

The exit-code model is part of the command contract:

| Status | fail-on-warning | Exit code |
|---|---:|---:|
| `passed` | false/true | 0 |
| `passed_with_warnings` | false | 0 |
| `passed_with_warnings` | true | 1 |
| `blocked` | false/true | 1 |

## Output stability

The JSON report must preserve the M67 top-level shape:

```text
mode
status
profile
package_root
checks
warnings
errors
summary
exit_code
```

Future additions are allowed only when backwards-compatible.

## Repo-level hygiene readiness

Repo-level hygiene may aggregate clean-check reports, but must not automatically enforce applied-package checks without explicit ownership policy.

## Non-goals

This model does not define:

- package repair;
- runtime regeneration;
- lockfile regeneration;
- compiler behavior;
- opcodes;
- natural-language authority classifiers;
- applied-package migration.
