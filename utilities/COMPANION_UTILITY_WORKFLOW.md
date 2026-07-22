# M61.3 — Companion Utility Workflow Guide

Status: **stable docs consolidation**.  
Base: **M61.2 Visual Graph Generator Package Import**.  
Scope: explain the combined read-only utility route across Visual Graph Generator and PathWalk.  
Non-scope: runtime execution, scoring, calibration, benchmark orchestration, watchdog/process-boundary hardening, and merging utilities into one program.

## Purpose

M61.3 turns the included companion utilities into one practical author/reviewer workflow. It does not add new feature behavior. It answers one question:

```text
After I have source/program.ordo.yaml, which utility do I run first, and what artifact do I inspect next?
```

## Stable companion utility route

```text
source/program.ordo.yaml
  → Visual Graph Generator: inspect the structure visually
  → PathWalk real-module-graph: summarize source YAML as graph data
  → PathWalk real-module-paths: enumerate terminal paths
  → PathWalk real-module-clean-cases: generate clean-path testcase artifacts
  → PathWalk real-module-noise-cases: generate bounded-noise testcase artifacts
  → PathWalk real-module-review-cards: generate human QA/developer review cards
  → Visual Graph annotation overlay: optionally highlight review/debug notes
```

## Utility responsibilities

| Utility | Reads | Writes | Main question | Runtime role |
|---|---|---|---|---|
| Visual Graph Generator | Ordo YAML/IR | `.mmd`, `.svg`, `.png`, overlay reports | What does the tree look like? | None; read-only renderer |
| PathWalk | Ordo source YAML or PathWalk artifacts | graph summaries, paths, cases, review cards | What paths/cases/cards should a reviewer inspect? | None in the M60.7/M61.0 artifact-only line |
| Ordo runtime CLI | runtime packages | session/state/runtime artifacts | Did an actual runtime session progress correctly? | Runtime core |

## Quickstart: visual-first review route

Use a real module source file:

```bash
SRC=source/program.ordo.yaml
RUN=runs/companion_review
mkdir -p "$RUN"
```

### 1. Render a full visual graph

Mermaid:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py   "$SRC"   --format mmd   --out "$RUN/full_graph.mmd"
```

SVG, when Graphviz `dot` is installed:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py   "$SRC"   --format svg   --out "$RUN/full_graph.svg"
```

Use this before generating cases when the author/reviewer needs a fast visual sanity check.

### 2. Summarize the real module graph

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-graph   --source "$SRC"   --out "$RUN/graph"   --force
```

Important artifacts:

```text
$RUN/graph/REAL_MODULE_GRAPH_SUMMARY.json
$RUN/graph/REAL_MODULE_GRAPH_SUMMARY.md
$RUN/graph/VALIDATION_REPORT.json
```

### 3. Enumerate terminal paths

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-paths   --summary "$RUN/graph/REAL_MODULE_GRAPH_SUMMARY.json"   --out "$RUN/paths"   --force
```

Important artifacts:

```text
$RUN/paths/REAL_MODULE_TERMINAL_PATHS.json
$RUN/paths/REAL_MODULE_TERMINAL_PATHS.md
```

### 4. Generate clean-path testcase artifacts

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-clean-cases   --paths "$RUN/paths/REAL_MODULE_TERMINAL_PATHS.json"   --out "$RUN/clean_cases"   --force
```

Important artifacts:

```text
$RUN/clean_cases/cases/*.json
$RUN/clean_cases/cases/*.md
$RUN/clean_cases/RAW_TESTCASE_MATRIX.csv
$RUN/clean_cases/SUMMARY.json
$RUN/clean_cases/SUMMARY.md
```

### 5. Generate bounded-noise testcase artifacts

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-noise-cases   --paths "$RUN/paths/REAL_MODULE_TERMINAL_PATHS.json"   --out "$RUN/noise_cases"   --force
```

M61.3 keeps the M60.7 line closure boundary: default bounded noise patterns are:

```text
distraction
invalid_branch
clarification_without_submit
skip_ahead
```

`backtrack` and `correction_backtrack` remain future improvements.

### 6. Generate human review scenario cards

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-review-cards   --summary "$RUN/clean_cases/SUMMARY.json"   --summary "$RUN/noise_cases/SUMMARY.json"   --out "$RUN/review_cards"   --force
```

Important artifacts:

```text
$RUN/review_cards/cards/*.md
$RUN/review_cards/REVIEW_CARDS.md
$RUN/review_cards/RAW_REVIEW_CARD_MATRIX.csv
$RUN/review_cards/VALIDATION_REPORT.json
```

### 7. Optional annotation overlay

Use annotation overlays when a reviewer wants to highlight newly added nodes, risky branches, suspicious gates, or review comments on a graph.

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph_annotation_demo.py   "$SRC"   --annotations utilities/ordo_visual_graph_generator/examples/demo_support_triage.annotations.v1.json   --out "$RUN/annotated_graph.svg"
```

The annotation schema is documented in:

```text
utilities/ordo_visual_graph_generator/ANNOTATION_OVERLAY_SCHEMA.md
```

## Recommended inspection order

For authoring and QA, inspect artifacts in this order:

1. `full_graph.svg` or `full_graph.mmd` — visual sanity check.
2. `REAL_MODULE_GRAPH_SUMMARY.md` — structural summary.
3. `REAL_MODULE_TERMINAL_PATHS.md` — path coverage.
4. `SUMMARY.md` from clean/noise cases — testcase inventory.
5. `REVIEW_CARDS.md` — human-facing scenario cards.
6. Annotation overlay graph — comments/highlights for review sessions.

## What M61.3 does not claim

M61.3 artifacts are not runtime results. They do not prove that a model or runtime actually executed a testcase. They are author/reviewer artifacts only.

Explicitly out of scope:

- generated testcase execution;
- model/API benchmark runs;
- scoring and calibration;
- runtime-harness or matrix tests;
- watchdog/process-boundary hardening;
- merging Visual Graph Generator into PathWalk.

## Current stable handoff sentence

Use this sentence in package documentation:

```text
For Ordo authoring and review, use Visual Graph Generator first to inspect the YAML tree, then use PathWalk to enumerate terminal paths, generate clean and bounded-noise testcase artifacts, and create human review scenario cards. Both utilities remain companion tools and do not define runtime semantics.
```
