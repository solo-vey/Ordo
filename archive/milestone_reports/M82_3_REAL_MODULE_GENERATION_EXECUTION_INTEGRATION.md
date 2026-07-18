# M82.3 — Real-module testcase generation and hardened execution integration

## Status

`implemented / passed`

## Contract

M82.3 adds one explicit orchestration boundary over the existing real-module generators and the M82.1/M82.2 hardened execution stack.

Supported modes:

- `generate-only` — writes graph, terminal paths, and selected testcase packages; no worker process is started and no execution directory is created.
- `generate-and-run` — performs the same generation, creates immutable execution plans, starts every testcase through a separate `real-module-exec-job` worker process, and collects versioned M82.2 evidence.

Supported case sets:

- `clean`
- `noise`
- `both`

The orchestration process never calls testcase runtime execution in-process. Worker stdin is closed, worker environment is reduced, and execution remains governed by the M82.1 watchdog and isolation contract.

## CLI

    PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-pipeline \
      --source path/to/source/program.ordo.yaml \
      --out runs/real_module_pipeline \
      --mode generate-only \
      --case-set clean

    PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-pipeline \
      --source path/to/source/program.ordo.yaml \
      --out runs/real_module_pipeline \
      --mode generate-and-run \
      --case-set both \
      --pattern distraction \
      --timeout 30 \
      --cleanup-policy retain_failures

## Primary artifact

`REAL_MODULE_PIPELINE_MANIFEST.json` links:

- source module;
- graph and path generation outputs;
- clean/noise testcase summaries;
- execution plans;
- worker launch results;
- execution summaries and M82.2 evidence claims.

## Claim boundary

M82.3 claims generation and raw execution evidence only. It does not perform scoring or calibration.

## Acceptance

- generate-only creates testcase artifacts without execution: PASS
- generate-and-run uses separate worker processes: PASS
- clean suite end-to-end execution and evidence collection: PASS
- clean/noise suite selection: PASS
- non-empty output protection: PASS
- M82.1/M82.2/M76.2 regression: PASS
