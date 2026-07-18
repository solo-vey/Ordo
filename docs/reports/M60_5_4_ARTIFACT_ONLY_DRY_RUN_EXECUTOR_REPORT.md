# M60.5.4 Artifact-only Dry-run Executor Report

Status: passed as a PathWalk orchestration patch. No Ordo runtime-core semantics were changed.

## Problem

Previous dry-run orchestration attempted to execute many benchmark cases through
long-lived parent loops. In constrained agent/shell environments this could
appear to hang even after a worker had already produced its score artifact.

## Decision

M60.5.4 makes benchmark execution artifact-oriented:

1. `dry-run-plan` creates a declarative `DRY_RUN_PLAN.json`.
2. It also materializes immutable `jobs/*.json` descriptors.
3. It creates one-job shell wrappers in `job_scripts/*.sh`.
4. Each job is intended to run independently from shell/CI/external supervisor.
5. `dry-run-collect` aggregates existing `*_score.json` files.

## Acceptance evidence

- PathWalk pytest: 22/22 passed.
- `py_compile`: passed for `cli/` and `ordo_pathwalk/` Python files.
- Artifact-only sample: one scenario across `json`, `ordo-code`, and `json,ordo-code` produced three passing score files and a passing `SUMMARY.json`.

## Non-goals

- No score weight calibration.
- No real model/API benchmark.
- No Ordo runtime-core semantic changes.
- No MCP/sandbox changes.
