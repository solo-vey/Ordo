# CI workflow implementation

Status: `M69.1 implemented`

M69.1 adds a dedicated GitHub Actions workflow for the Ordo language repository:

```text
.github/workflows/ordo-clean-gate.yml
```

The workflow is intentionally separate from the pre-existing broad `ordo-check.yml`. This preserves the previous workflow behavior and makes the clean gate independently reviewable.

## Trigger and policy mapping

| Trigger | Profile | fail-on-warning | Evidence path |
|---|---|---:|---|
| pull request | `standard` | false | `reports/ci/repo_clean_check.json` |
| push to `main` or `master` | `standard` | true | `reports/ci/repo_clean_check.json` |

## Execution rule

The workflow calls the installed CLI and does not reproduce hygiene logic:

```bash
ordo repo-check . --clean --profile standard --json --out reports/ci/repo_clean_check.json
```

For the default branch, it additionally supplies `--fail-on-warning`.

The shell uses `set -euo pipefail`, so piping JSON through `tee` does not hide a non-zero CLI exit code.

## Evidence retention

The underlying JSON report and captured stdout JSON are uploaded through `actions/upload-artifact@v4`, even when the gate fails. Retention is 14 days for this first implementation wave.

## Deliberate exclusions

M69.1 does not:

- add release or tag triggers;
- change `repo-check` or `clean-check` implementation;
- create a second hygiene engine in workflow shell;
- modify applied packages;
- add auto-fix or regeneration behavior.

Release candidate and release integration remain M69.2 scope.
