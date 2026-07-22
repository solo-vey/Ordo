# M60.8 — Stable Developer Handoff Consolidation

Status: **stable handoff base**.

M60.8 is a documentation/package-consolidation milestone. It does not add language semantics, runtime-core behavior, scoring changes, model/API benchmark behavior, or new PathWalk generator features. Its job is to make the current stable developer-facing package understandable after the M60.6 and M60.7 milestone sequence.

## Current stable base

Use this package line as the current stable developer handoff:

```text
M60.6.4  = stable benchmark-prep / transcript-replay pilot base
M60.7.5  = stable artifact-only real-module testcase generation base
M60.7 LC = stable line closure boundary
M60.8    = stable handoff consolidation, docs-only
```

The stable source-level testcase generation flow is:

```text
source/program.ordo.yaml
  -> REAL_MODULE_GRAPH_SUMMARY.json/.md
  -> REAL_MODULE_TERMINAL_PATHS.json/.md
  -> clean path cases
  -> bounded noise cases
```

## What is stable

### Ordo runtime / language

- M60 multi-target runtime contract remains unchanged.
- Canonical rule remains:

```text
JSON IR decides.
Ordo-code explains.
Session-trace proves.
```

- Runtime-core semantics are unchanged in M60.8.
- Scoring weights are unchanged in M60.8.
- Generated real-module testcase artifacts are source-level artifacts, not runtime-executed benchmark results.

### PathWalk artifact-only real-module flow

Run these from a workspace or from PathWalk RC with developer bundle CLI on `PYTHONPATH`.

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-graph   --source utilities/ordo_pathwalk/examples/m60_7_5_remaining_noise_testcases/source/program.ordo.yaml   --out runs/real_module_graph   --force

PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-paths   --summary runs/real_module_graph/REAL_MODULE_GRAPH_SUMMARY.json   --out runs/real_module_paths   --force

PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-clean-cases   --paths runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json   --out runs/real_module_clean_cases   --force

PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-noise-cases   --paths runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json   --out runs/real_module_noise_cases   --pattern distraction   --pattern invalid_branch   --pattern clarification_without_submit   --pattern skip_ahead   --force
```

Generated artifacts are intended for review, QA planning, and future benchmark preparation. They are not proof of model quality by themselves.

## Supported bounded noise patterns

M60.8 keeps the M60.7.5 boundary:

```text
distraction
invalid_branch
clarification_without_submit
skip_ahead
```

Complex conversational recovery patterns are deferred:

```text
backtrack
correction_backtrack
```

Those are useful, but they should not reopen the M60.7 noise-expansion line. They belong to a future milestone with a stronger reason and explicit scope.

## Known blocked / experimental branches

Do not use the following as stable bases:

```text
M60.6.5   = blocked-no-release transcript replay acceptance matrix experiment
M60.6.4.1 = blocked-no-release process-boundary hardening experiment
```

Reason: multi-runtime transcript replay / embedded runtime verification can hang around child-process / `verify-session` boundaries in the current sandbox-style orchestration. That is not a blocker for the M60.7 artifact-only flow.

## What not to do as part of this handoff

Do not treat M60.8 as approval to start an unbounded hardening loop. In particular, avoid using these as release gates until a future milestone explicitly owns them:

- runtime-harness matrix tests;
- transcript-replay multi-runtime acceptance matrix;
- model/API benchmark orchestration;
- generated testcase runtime execution;
- scoring and calibration for generated real-module cases;
- watchdog/process-boundary hardening.

## Recommended next milestones

The current stable path is closed enough for handoff. Future work should be explicit and separate:

```text
M61.0 — Human Review Scenario Cards
M62.0 — Runtime Execution of Generated Testcases
```

See `backlog/FUTURE_BACKLOG.md`.
