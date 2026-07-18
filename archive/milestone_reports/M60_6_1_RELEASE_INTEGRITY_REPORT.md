# M60.6.1 Release Integrity / Handoff Hardening Report

Status: **passed-with-notes**  
Date: 2026-07-07

## Scope

M60.6.1 is a clean-room release-integrity patch on top of M60.6. It does not change runtime-core semantics, scoring weights, or the M60.6 calibration-preparation metrics.

## Checks performed

| Check | Result |
|---|---|
| Clean-room extraction of M60.6 archives | passed |
| Original M60.6 workspace `py_compile` | passed |
| Original M60.6 workspace PathWalk pytest | 22/22 passed |
| Original PathWalk RC v9.6 + developer-bundle CLI pytest | 22/22 passed |
| Archived M60.6 dry-run artifact recollect | 60/60 passed |
| Book source generated-output hygiene | passed; no PDF/DOCX/PPTX outputs found |
| Patched M60.6.1 `py_compile` | passed |
| Patched M60.6.1 workspace PathWalk pytest | 22/22 passed |
| Patched PathWalk RC v9.6.1 + developer-bundle CLI pytest | 22/22 passed |
| Patched standalone RC + developer-bundle generated job-script smoke | 3/3 passed |
| Missing CLI fail-fast check | passed; exits with status 65 and actionable message |

## Issues found

1. **M6061-I01 — generated job scripts embedded a temporary absolute workspace path.**  
   In M60.6 artifacts, `job_scripts/*.sh` could contain an absolute path from the generation machine, including an M60.5.4 workspace path. This made job scripts non-portable after clean-room extraction unless `ORDO_PATHWALK_ROOT` was overridden.

2. **M6061-I02 — stale PathWalk RC README wording.**  
   The RC archive name was v9.6 / M60.6, but root README still said v9.5 / M60.5.4.

3. **M6061-I03 — compact evidence archive is not a standalone re-execution bundle.**  
   The compact M60.6 baseline archive contained score artifacts and job descriptors, but not `runtime_templates/`. It is valid as evidence/recollect input, but full re-execution requires either the full plan directory or regenerating a plan from PathWalk.

## Fixes applied

- `ordo_pathwalk/runner/dry_run.py` now generates portable job scripts.
- Job scripts now use:

```bash
export ORDO_PATHWALK_ROOT=<workspace-or-pathwalk-rc-root>
export ORDO_CLI_ROOT=<developer-bundle-root>/cli  # needed when PathWalk root has no cli/ordo
```

- Job scripts fail fast if `ordo_pathwalk/` or `cli/ordo/` is missing.
- Existing packaged `job_scripts/*.sh` in workspace/developer bundle examples and report mirrors were patched to the same portable contract.
- `JOB_EXECUTION.md`, workspace README/CHANGELOG, PathWalk RC README, and book source notes were updated.

## What did not change

- Default scoring weights: **not changed**.
- Runtime-core semantics: **not changed**.
- M60.6 `RAW_METRICS.csv` and summary metrics: **not recalibrated**.
- Real model/API benchmark: **not run**.

## Readiness decision

M60.6.1 is ready as a release-integrity/handoff hardening patch. It should replace M60.6 handoff archives before moving to M60.6.2 calibration report refinement or M60.7/M61 real-module testcase generation.
