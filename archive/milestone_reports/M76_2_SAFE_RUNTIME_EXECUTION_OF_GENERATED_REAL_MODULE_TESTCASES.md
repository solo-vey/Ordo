# M76.2 — Safe Runtime Execution of Generated Real-Module Testcases

## Status

`implemented / passed`

## Contract

Generated real-module testcase execution uses an artifact-oriented process boundary:

1. `real-module-exec-plan` creates immutable job descriptors and one-job shell wrappers.
2. Every testcase runs in one short-lived child process.
3. Every child receives an isolated sandbox containing a copied source module, minimal package manifest, answers and runtime evidence.
4. A hard watchdog applies per invocation and terminates the full process group on timeout.
5. The parent collector reads result artifacts only; it does not execute cases.
6. Runtime execution produces raw evidence only. Scoring and calibration remain separate claims.

## CLI

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-exec-plan \
  --summary <testcase-package>/SUMMARY.json \
  --source <module>/source/program.ordo.yaml \
  --out runs/real_module_execution \
  --timeout 30

bash runs/real_module_execution/job_scripts/EXEC_<CASE_ID>.sh

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-exec-collect \
  --plan runs/real_module_execution/REAL_MODULE_EXECUTION_PLAN.json
```

## Safety properties

- no in-process testcase execution by planner/collector;
- stdin closed for workers;
- separate process group;
- CPU, file-size and open-file limits where supported;
- bounded stdout/stderr evidence;
- deterministic timeout evidence;
- source copied into sandbox;
- no direct `compiled/*` read;
- no scoring/calibration claim.

## Acceptance

- child-process boundary: PASS
- hard watchdog: PASS
- isolated execution directory: PASS
- collect-only parent: PASS
- deterministic result evidence: PASS
- fixture execution: 3/3 PASS
- regression tests: 4/4 PASS
