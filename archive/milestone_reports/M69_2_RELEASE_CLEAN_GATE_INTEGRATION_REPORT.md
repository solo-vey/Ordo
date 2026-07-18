# M69.2 — Release Clean Gate Integration Report

Status: `implemented-release-gate / passed-validation`

## Scope

Implemented a separate release clean-gate workflow for the Ordo language repository. The workflow invokes the existing `ordo repo-check --clean` engine with the accepted release policy.

## Added

- `.github/workflows/ordo-release-clean-gate.yml`
- `cli/docs/RELEASE_CLEAN_GATE_INTEGRATION.md`
- `cli/tests/test_release_clean_gate_workflow.py`
- M69.2 machine-readable reports and intake copies

## Policy

- trigger: pushed `v*` tag or manual dispatch;
- profile: `strict`;
- fail on warning: enabled;
- report: `reports/release/repo_clean_check.json`;
- evidence retention: 90 days.

## Boundaries

No package-local files, runtime semantics, compiler behavior, opcodes, compiled IR, lockfiles, embedded CLI bundles, or release archive commands were changed.
