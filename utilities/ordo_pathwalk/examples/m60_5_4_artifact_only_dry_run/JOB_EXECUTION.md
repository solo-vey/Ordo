# PathWalk dry-run job execution

This directory uses the M60.6.1 artifact-only dry-run execution contract.

Recommended execution model:

1. `DRY_RUN_PLAN.json` declares the full benchmark matrix.
2. `jobs/*.json` are immutable one-job descriptors.
3. `job_scripts/*.sh` executes exactly one job and redirects stdin from `/dev/null`.
4. Run jobs independently from a shell, CI matrix, or external supervisor.
5. After jobs finish, run `python3 -m utilities.ordo_pathwalk.cli dry-run-collect --plan DRY_RUN_PLAN.json`.

Do not use a long-lived Python parent process as the acceptance path for multi-job dry-runs.

Portable execution note: job scripts no longer embed a generation-machine workspace path. If scripts are not inside a full Ordo workspace, set `ORDO_PATHWALK_ROOT` to a workspace or PathWalk RC root. If that root does not contain `cli/ordo`, also set `ORDO_CLI_ROOT` to the developer bundle `cli/` directory.

