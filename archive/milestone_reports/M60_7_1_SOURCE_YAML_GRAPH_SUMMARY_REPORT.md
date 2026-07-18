# M60.7.1 — Source YAML Loader and Real Module Graph Summary

## Status

`passed-implementation-slice`

## Scope

M60.7.1 implements the first narrow slice of Real Module Testcase Generation:

```text
source/program.ordo.yaml → REAL_MODULE_GRAPH_SUMMARY.json/.md → VALIDATION_REPORT.json
```

This is authoring/testcase-generation analysis. It may read `source/program.ordo.yaml`, but it does not read `compiled/*` and it does not change enforced runtime rules.

## Implemented

- Added `ordo_pathwalk/generator/real_module.py`.
- Added PathWalk CLI command:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-graph \
  --source path/to/source/program.ordo.yaml \
  --out runs/real_module_graph \
  --force
```

- Added generated artifacts:
  - `REAL_MODULE_GRAPH_SUMMARY.json`
  - `REAL_MODULE_GRAPH_SUMMARY.md`
  - `VALIDATION_REPORT.json`
- Added neutral sample under `ordo_pathwalk/examples/m60_7_1_real_module_graph_summary/`.
- Added pytest coverage for loader, artifact writer, and CLI.
- Updated PathWalk README / CHANGELOG / real-module design doc.
- Updated book source chapter 61 only; no PDF/book generation.

## Graph summary contents

The graph summary extracts:

- package metadata;
- start node and start candidates;
- nodes, questions, answer types and allowed answers;
- answer edges and branch labels;
- unmatched-input handlers;
- gate/output/terminal/unresolved targets;
- gate and output summaries;
- readiness fields separating graph summary readiness from testcase generation readiness.

## Smoke result

Neutral sample smoke:

```text
nodes: 2
edges: 4
branching_nodes: 1
linear_nodes: 1
gates: 1
outputs: 1
unmatched_handlers: 2
graph_summary_ready: true
path_enumeration_ready: true
testcase_generation_ready: false
```

## Validation

Passed:

- `python3 -m compileall -q ordo_pathwalk cli/ordo`
- selected non-runtime PathWalk pytest: `14 passed`
- CLI smoke: `real-module-graph` produced all expected artifacts
- book source manifest sanity: passed

Not used as gate:

- broad runtime-harness / transcript-replay matrix tests, because that is the known M60.6.5 / M60.6.4.1 blocker branch and is not relevant to this source-loader implementation slice.

## Non-goals preserved

- No testcase generation yet.
- No terminal-path enumeration yet.
- No scoring weight calibration.
- No real API/model benchmark.
- No Ordo runtime-core semantic changes.
- No PDF/book generation.

## Next step

M60.7.2 — Terminal Path Enumeration.

Recommended boundary for M60.7.2:

```text
REAL_MODULE_GRAPH_SUMMARY.json → terminal_paths[] → no testcase/noise generation yet
```

Stop condition for M60.7.2: if terminal path enumeration starts requiring broad runtime execution or benchmark orchestration, stop and mark it as a future improvement instead of continuing into micro-hardening.
