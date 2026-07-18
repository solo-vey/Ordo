# Repo-check `--clean` Integration

Status: `M68.4 implemented / optional integration`

M68.4 adds an optional repo-level hygiene aggregation mode to the existing `repo-check` command:

```bash
ordo repo-check <repo> --clean
ordo repo-check <repo> --clean --profile light|standard|strict
ordo repo-check <repo> --clean --fail-on-warning
ordo repo-check <repo> --clean --json
ordo repo-check <repo> --clean --out reports/repo_check_report.json
```

The existing `ordo repo-check <repo>` behavior remains unchanged when `--clean` is not supplied.

## Boundary

`clean-check` remains the package-level source of truth. `repo-check --clean` only aggregates package-level clean reports according to an explicit repo hygiene policy.

It is read-only and does not:

- repair packages;
- regenerate runtime artifacts;
- regenerate lockfiles;
- rebuild embedded CLI bundles;
- apply standards to applied packages by default.

## Policy file

`repo-check --clean` looks for one of these files in the repo root:

```text
repo_hygiene.yml
repo_hygiene.yaml
ordo_repo_hygiene.yml
ordo_repo_hygiene.yaml
```

Example:

```yaml
repo_hygiene:
  default_profile: standard
  fail_on_warning: false
  roots:
    - root_id: language_like_root
      path: language_like_root
      role: language_core
      clean_check: required
      release_blocking: true
    - root_id: applied_packages
      path: packages
      role: applied_package
      clean_check: delegated
      release_blocking: false
```

## Missing policy behavior

If no policy exists, `repo-check --clean` does not wide-enforce discovered packages. It returns a `repo_package_hygiene` section with `status: not_applicable` and reports package roots under `packages/` as delegated.

## Report shape

The existing repo-check report gains an optional section:

```json
{
  "reports": {
    "workflow_paths": {},
    "generated_metadata_absent": {},
    "package_generated_artifacts_absent": {},
    "repo_package_hygiene": {
      "schema_version": "ordo.repo_hygiene.report.v1",
      "mode": "repo_package_hygiene",
      "status": "passed|passed_with_warnings|blocked|not_applicable",
      "roots": [],
      "delegated_roots": [],
      "warnings": [],
      "errors": [],
      "summary": {},
      "exit_code": 0
    }
  }
}
```

## Aggregation

- `blocked` on a release-blocking required root blocks repo-check.
- `passed_with_warnings` blocks only when the root is release-blocking and `--fail-on-warning` is used.
- `delegated` roots are reported but not checked.
- Missing policy is non-blocking and `not_applicable`.
