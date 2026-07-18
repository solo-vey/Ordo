# Release Clean Gate Integration

Status: `M69.2 implemented`

M69.2 connects the M69.0 release policy to GitHub Actions without adding a second hygiene engine.

## Workflow

`.github/workflows/ordo-release-clean-gate.yml`

Triggers:

- a pushed version tag matching `v*`;
- manual `workflow_dispatch`.

The workflow runs the existing repository hygiene command:

```bash
ordo repo-check . \
  --clean \
  --profile strict \
  --fail-on-warning \
  --json \
  --out reports/release/repo_clean_check.json
```

The workflow trusts the CLI exit code. It does not inspect package files itself, recalculate statuses, or repair artifacts.

## Evidence

The workflow uploads:

- `reports/release/repo_clean_check.json` — source-of-truth CLI report;
- `reports/release/repo_clean_check.stdout.json` — captured JSON stdout;
- `reports/release/release_clean_gate_provenance.json` — wrapper metadata containing revision, ref, run id, profile and warning policy.

Release evidence retention is 90 days. The wrapper provenance does not rewrite the CLI report.

## Boundary

Applied packages remain delegated unless the repository hygiene policy explicitly opts them into the release scope. The workflow does not mutate `packages/*`, compile IR, rebuild embedded CLI bundles, or create release archives.
