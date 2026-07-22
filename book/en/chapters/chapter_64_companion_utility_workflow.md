# Chapter 64. Shared Workflow for Companion Utilities

M61.3 defines a simple practical workflow for utilities that accompany Ordo. This is not a runtime layer or benchmark runner. It is an author/reviewer layer: first inspect the tree, then generate path/case/card artifacts, and then, when needed, highlight comments on the graph.

## Why a separate workflow is needed

After M61.2, the package contains two different companion utilities:

```text
Visual Graph Generator
  → shows an Ordo YAML/IR tree as Mermaid/SVG/PNG

PathWalk
  → creates graph summaries, terminal paths, clean/noise cases, and review cards
```

If they are merely placed side by side without a workflow, a package user may not immediately understand where to start. M61.3 answers that question.

## Recommended order

```text
source/program.ordo.yaml
  → Visual Graph Generator: inspect the tree
  → PathWalk real-module-graph: obtain a structural summary
  → PathWalk real-module-paths: inspect terminal paths
  → PathWalk real-module-clean-cases: create clean-path cases
  → PathWalk real-module-noise-cases: create bounded-noise cases
  → PathWalk real-module-review-cards: create readable scenario cards
  → Visual Graph annotation overlay: highlight comments or problematic areas
```

## What to inspect first

For an author or reviewer, the best first artifact is the graph:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py \
  source/program.ordo.yaml \
  --format svg \
  --out runs/companion_review/full_graph.svg
```

If Graphviz is unavailable, create Mermaid:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py \
  source/program.ordo.yaml \
  --format mmd \
  --out runs/companion_review/full_graph.mmd
```

## Next: PathWalk artifacts

After visual review, structural review artifacts can be created:

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-graph \
  --source source/program.ordo.yaml \
  --out runs/companion_review/graph \
  --force
```

Then terminal paths:

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-paths \
  --summary runs/companion_review/graph/REAL_MODULE_GRAPH_SUMMARY.json \
  --out runs/companion_review/paths \
  --force
```

Then clean/noise cases and human review cards.

## What this does not prove

This workflow does not prove that a model executed a testcase. It does not run the runtime or score model behavior. It gives a human understandable artifacts for analysis.

This is a fundamental boundary:

```text
visual/review artifacts ≠ runtime execution results
```

## Stable boundary

At M61.3, the companion-utility layer has a complete practical form:

```text
Visual Graph Generator + PathWalk = author/reviewer toolkit
```

Runtime execution of generated testcases remains a separate future milestone, not part of this workflow.
