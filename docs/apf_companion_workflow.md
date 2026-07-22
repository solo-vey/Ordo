# M62.2 — APF + Companion Utilities Workflow

Status: documentation guide.  
Date: 2026-07-08

This document connects the standard APF module with the companion utilities imported earlier.

## One route for APF reviewers

```text
packages/ordo_applied_project_factory/source/program.ordo.yaml
  → Ordo CLI lint / compile / test
  → Visual Graph Generator for context/full/path SVG or Mermaid views
  → PathWalk real-module-graph for graph summary
  → PathWalk real-module-paths for terminal paths
  → PathWalk real-module-clean-cases / real-module-noise-cases
  → PathWalk real-module-review-cards
```

## Why this route exists

APF is a self-hosted authoring process. That makes it easy to lose orientation: the reviewer may be reviewing the future process, a node in the authoring tree, a validation gate, or an output-template decision.

The combined route gives three complementary views:

```text
Visual Graph → where am I in the tree?
PathWalk → what terminal paths and review cases exist?
APF docs/source → what is the authoritative package contract?
```

## Source of truth

```text
source/program.ordo.yaml decides module structure.
compiled/program.ir.json is generated from source and must not be edited manually.
Visual Graph and PathWalk artifacts are review aids.
```

## Useful APF commands

From the parent package root:

```bash
python -m cli.ordo.cli lint packages/ordo_applied_project_factory
python -m cli.ordo.cli compile packages/ordo_applied_project_factory
python -m cli.ordo.cli test packages/ordo_applied_project_factory
```

Then use utilities for inspection. Exact paths can vary by local checkout, but the stable workflow is:

```bash
python utilities/ordo_visual_graph_generator/ordo_graph.py \
  packages/ordo_applied_project_factory/source/program.ordo.yaml \
  --out runs/apf_visual/graph.mmd

PYTHONPATH=cli:. python -m utilities.ordo_pathwalk.cli real-module-graph \
  --source packages/ordo_applied_project_factory/source/program.ordo.yaml \
  --out runs/apf_pathwalk/graph \
  --force
```

## Boundary

This is not runtime execution of generated testcases. It is a review/documentation workflow for the APF module itself.

## APF-specific PathWalk note

The full companion route (`graph → paths → clean/noise cases → review cards`) is the stable route for source-level packages whose terminal paths can be enumerated without unresolved cycles.

For the imported APF `v0.1.0-alpha.14` package specifically:

```text
Visual Graph Mermaid/SVG smoke: verified
PathWalk real-module-graph smoke: verified
PathWalk real-module-paths: blocked by cycle edges in current APF authoring loop
PathWalk clean/noise/review-card generation for APF itself: not used as M62.2 gate
```

This is expected for M62.2 because APF is a self-hosted authoring process with review loops. Cycle-aware terminal path handling or APF-specific graph adaptation belongs to a later APF adaptation milestone, not this documentation milestone.
