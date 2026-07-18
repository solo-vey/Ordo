# Repo-Level Package Hygiene Design

Status: `M68.3 accepted design / no implementation`

M68.3 defines how repository-level hygiene should build on the package-level `ordo clean-check` command without changing applied packages or silently expanding ownership boundaries.

This is a design milestone only. It does not add a repo-level clean implementation.

## Purpose

Package-level `ordo clean-check <package>` answers whether one package root is clean, warning-only, blocked, or not applicable.

Repo-level hygiene answers a different question:

```text
Which roots in this repository are expected to be clean for this release scope,
which are delegated, which are draft, and which should block the repo-level gate?
```

Repo hygiene is therefore an aggregation and policy layer above clean-check. It must not replace package-level clean-check and must not mutate package contents.

## Design principles

1. `clean-check` remains the source of package-level truth.
2. Repo hygiene is read-only.
3. Repo hygiene must be opt-in for applied packages.
4. Delegated package roots are reported, not silently checked.
5. Stable language/CLI roots may be checked by default when repo policy declares them in scope.
6. Machine-readable evidence must be stable enough for CI and release gates.
7. Missing repo policy should not cause accidental wide enforcement.

## Candidate command shape

Preferred future extension:

```bash
ordo repo-check <repo> --clean
ordo repo-check <repo> --clean --profile standard
ordo repo-check <repo> --clean --json
ordo repo-check <repo> --clean --fail-on-warning
ordo repo-check <repo> --clean --out reports/repo_clean_check.json
```

Alternative kept in backlog:

```bash
ordo clean-check <repo> --repo
```

M68.3 chooses the `repo-check --clean` direction for future implementation because repo-level logic belongs with the existing repository checker.

## Repo hygiene policy object

A future implementation should accept an explicit repo hygiene policy. It may live in a dedicated file or a repo-level metadata section.

Example shape:

```yaml
repo_hygiene:
  policy_id: ordo_repo_hygiene_standard
  default_profile: standard
  fail_on_warning: false
  roots:
    - root_id: language_package
      path: language/
      role: language_core
      clean_check: required
      release_blocking: true
    - root_id: cli_package
      path: cli/
      role: cli_utility
      clean_check: required
      release_blocking: true
    - root_id: applied_modules
      path: packages/
      role: applied_packages
      clean_check: delegated
      release_blocking: false
```

## Root roles

| Role | Meaning | Default treatment |
|---|---|---|
| `language_core` | language docs, schemas, examples, specs | required for language release |
| `cli_utility` | CLI code, CLI docs, CLI tests | required for CLI release |
| `companion_utility` | utilities adjacent to the language | required only if release scope includes utility |
| `standard_applied_module` | package written in Ordo but maintained as a module | opt-in or delegated |
| `applied_package` | concrete customer/domain package | delegated by default |
| `book_or_docs` | derived docs/book artifacts | optional, release-scope dependent |
| `generated_artifact_area` | runtime/compiled/generated outputs | report drift; do not regenerate |

## Clean-check treatment values

| Value | Meaning |
|---|---|
| `required` | run clean-check and aggregate result |
| `optional` | run if root exists; warnings do not block unless configured |
| `delegated` | do not run by default; report as delegated |
| `ignored` | do not report except in debug/evidence mode |
| `not_applicable` | root is known but not clean-check compatible |

## Aggregation decision policy

Repo-level status is derived from per-root results and policy.

| Root result | Root release blocking | Repo effect |
|---|---:|---|
| `passed` | true/false | clean contribution |
| `passed_with_warnings` | false | warning contribution |
| `passed_with_warnings` | true and `fail_on_warning=false` | warning contribution |
| `passed_with_warnings` | true and `fail_on_warning=true` | blocked |
| `blocked` | true | blocked |
| `blocked` | false | warning unless policy escalates |
| `delegated` | false | delegated contribution |
| `not_applicable` | false | not-applicable contribution |

Repo-level status values:

```text
passed
passed_with_warnings
blocked
not_applicable
```

## Evidence report shape

A future implementation should produce a stable report shape:

```json
{
  "schema_version": "ordo.repo_hygiene.report.v1",
  "mode": "repo_package_hygiene",
  "status": "passed_with_warnings",
  "repo_root": "/abs/path/to/repo",
  "profile": "standard",
  "fail_on_warning": false,
  "roots": [],
  "delegated_roots": [],
  "warnings": [],
  "errors": [],
  "summary": {
    "root_count": 0,
    "checked_count": 0,
    "passed_count": 0,
    "warning_count": 0,
    "blocked_count": 0,
    "delegated_count": 0,
    "not_applicable_count": 0
  },
  "exit_code": 0
}
```

## Interaction with existing repo-check

Current `repo-check` already validates repository-level workflow paths and generated metadata hygiene. M68.3 does not change that behavior.

Future `repo-check --clean` should add a separate report section rather than mixing clean-check failures into existing checks without context:

```json
{
  "reports": {
    "workflow_paths": {},
    "generated_metadata_absent": {},
    "package_generated_artifacts_absent": {},
    "repo_package_hygiene": {}
  }
}
```

## Scope guard

Repo-level hygiene must not:

- modify files;
- run package repair;
- regenerate runtime artifacts;
- regenerate lockfiles;
- rebuild embedded CLI bundles;
- apply language standards to concrete packages automatically;
- check applied packages unless they are explicitly opted in by repo policy.

## M68.4 readiness criteria

Implementation may begin only if all are true:

1. Existing `repo-check` command can accept a `--clean` flag without breaking existing usage.
2. `clean_check.run_clean_check` can be called programmatically without subprocess-only assumptions.
3. Fixture tests can create synthetic repo roots outside `packages/`.
4. Applied packages remain opt-in or delegated.
5. JSON output and exit-code policy remain compatible with M68.2.
