# CI / Release Clean Gate Design

Status: `M69.0 accepted design / no workflow implementation`

M69.0 defines how the existing `ordo clean-check` and `ordo repo-check --clean` commands are consumed by CI and release processes of the Ordo language repository.

This milestone does not add GitHub Actions, does not change package contents, and does not introduce a second hygiene engine.

## Core rule

CI and release automation must call the existing CLI and trust its machine-readable report and exit code:

```text
CI/release trigger
  -> repo-check --clean
  -> stable JSON evidence
  -> existing CLI exit policy
  -> pass or block
```

Shell scripts and workflows must not reimplement package discovery, status aggregation, warning escalation, or clean-check rules.

## Gate classes

| Gate | Purpose | Default profile | fail-on-warning | Blocking scope |
|---|---|---|---:|---|
| `pull_request` | prevent structural regressions | `standard` | false | required roots only |
| `main_branch` | keep default branch continuously clean | `standard` | true | required roots only |
| `release_candidate` | verify release evidence before packaging | `strict` | true | release-blocking roots |
| `release` | final pre-release hygiene evidence | `strict` | true | release-blocking roots |
| `manual_audit` | diagnostic/manual review | configurable | configurable | policy-selected roots |

## Required behavior

1. The gate must run `ordo repo-check <repo> --clean`.
2. The gate must write a JSON report with `--out`.
3. The workflow result must follow the CLI exit code.
4. The report must be retained as evidence when the platform supports artifacts.
5. Applied packages remain delegated unless the repo policy opts them in.
6. Missing policy must not silently expand enforcement.
7. Release gates must record the selected profile and `fail_on_warning` value.

## Recommended commands

Pull request:

```bash
ordo repo-check . --clean --profile standard --json --out reports/ci/repo_clean_check.json
```

Release candidate / release:

```bash
ordo repo-check . --clean --profile strict --fail-on-warning --json --out reports/release/repo_clean_check.json
```

## Evidence contract

A gate evidence record must identify:

- gate id and gate class;
- repository revision when available;
- CLI command intent;
- selected profile;
- fail-on-warning policy;
- repo hygiene report path;
- report schema version;
- resulting status and exit code.

The gate wrapper may add provenance metadata, but it must not rewrite the underlying CLI report.

## Non-goals

M69.0 does not:

- create `.github/workflows/*`;
- modify `cli/ordo/*.py`;
- modify CLI tests;
- modify `packages/*`;
- change runtime/compiler/opcodes;
- define auto-repair or artifact regeneration;
- add release packaging behavior.

## M69.2 implementation note

The release gate is implemented as `.github/workflows/ordo-release-clean-gate.yml`. It uses the accepted `strict` plus `fail-on-warning` policy and preserves the CLI JSON report as release evidence.
