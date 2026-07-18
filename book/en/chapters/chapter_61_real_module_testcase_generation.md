# Chapter 61. Real Module Testcase Generation

## Why this step is needed

After M60.6, the dry-run baseline verifies wiring but does not provide enough diverse data for score calibration.

The next useful step is not immediately a large model benchmark. It is to teach PathWalk to build test cases from a real Ordo module.

The M60.7 idea is:

```text
real source/program.ordo.yaml
        ↓
real decision tree / graph
        ↓
terminal paths
        ↓
testcase artifacts
        ↓
controlled noise
```

## Input

The basic input is:

```text
source/program.ordo.yaml
```

PathWalk may read source YAML for testcase generation because this belongs to the authoring and testing layer.

During enforced runtime execution, however, the model still must not read `compiled/*` directly. It must use the embedded CLI.

## Required noise types

M60.7 must generate more than ideal happy paths. Controlled confusion patterns are needed:

| Type | Meaning |
|---|---|
| `clean_path` | correct branch traversal without noise |
| `distraction` | unrelated question during intake |
| `backtrack` | return to a previous node |
| `skip_ahead` | attempt to answer a future step too early |
| `invalid_branch` | answer not allowed by the current branch |
| `clarification_without_submit` | clarification without a submitted answer |
| `correction_backtrack` | correction of an earlier submitted answer |

## Generated artifacts

The initial generation contract includes:

```text
REAL_MODULE_TESTCASE_PLAN.json
REAL_MODULE_GRAPH_SUMMARY.json
cases/<case_id>.json
cases/<case_id>.md
RAW_TESTCASE_MATRIX.csv
SUMMARY.json
SUMMARY.md
VALIDATION_REPORT.json
```

This is a testcase-generation contract, not yet a model-benchmark contract.

## What must not be mixed

M60.7 must not silently become runtime execution, scoring, or calibration.

The layers are different:

```text
generate cases
review cases
execute cases
score execution
calibrate benchmark
```

Each needs its own evidence boundary.

## M60.7.1 and M60.7.2

The first steps establish real-module graph extraction and terminal-path enumeration. The generator derives a graph summary and explicit terminal paths from the source module.

Later steps generate clean-path cases and bounded-noise variants.

## Supported bounded-noise line

The completed artifact-only line supports:

```text
distraction
invalid_branch
clarification_without_submit
skip_ahead
```

More complex conversational recovery patterns, especially `backtrack` and `correction_backtrack`, are not automatically promoted in this line. They remain future improvements so M60.7 does not become an endless block of incremental behavior work.

## Correct sequence

The stable sequence is:

```text
source/program.ordo.yaml
        ↓
REAL_MODULE_GRAPH_SUMMARY
        ↓
REAL_MODULE_TERMINAL_PATHS
        ↓
clean-path testcase artifacts
        ↓
bounded-noise testcase artifacts
```

Runtime execution, scoring, and benchmark orchestration remain separate milestones.

## M60.7 closure

M60.7 closes at a stable artifact-only boundary. The generator can produce structured, reviewable cases from a real module without claiming that those cases were executed by a model.

That distinction is important:

```text
generated testcase != executed testcase
review-ready != runtime-verified
```
