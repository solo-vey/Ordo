# M61 Line Closure

M61 is closed as the stable companion-utility line. Use the M61 Line Closure archives for handoff when the user needs the complete Visual Graph + PathWalk workflow. Runtime execution, scoring, calibration, and additional noise variants remain future work.

See `M61_LINE_CLOSURE_REPORT.md` and `M61_COMPANION_UTILITIES_LINE_CLOSURE.md`.

---

# Ordo Companion Utilities

This directory contains optional utilities that ship beside Ordo but do not define Ordo runtime semantics.

## Current status

M61.2 imports the Visual Graph Generator as a second included companion utility.

## Utilities

| Utility | Package location | Purpose | Status |
|---|---|---|---|
| PathWalk | `ordo_pathwalk/` | Real-module graph summaries, terminal paths, clean/noise testcase artifacts, human review cards | Included |
| Visual Graph Generator | `utilities/ordo_visual_graph_generator/` | Render Ordo YAML/IR as `.mmd`, `.svg`, `.png`; support subtree/context/path views and annotation overlays | Included as of M61.2 |

## Rule

Utilities may read Ordo YAML/IR and generate review, debug, test, or visual artifacts. They must not silently change runtime-core behavior.

## Visual Graph Generator quickstart

Generate Mermaid:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py \
  utilities/ordo_visual_graph_generator/examples/demo_support_triage.ordo.yaml \
  --format mmd \
  --out runs/visual_graph/demo_support_triage.mmd
```

Generate SVG when Graphviz `dot` is installed:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py \
  utilities/ordo_visual_graph_generator/examples/demo_support_triage.ordo.yaml \
  --format svg \
  --out runs/visual_graph/demo_support_triage.svg
```

See `utilities/ordo_visual_graph_generator/README.md` and `utilities/ordo_visual_graph_generator/ORDO_INTEGRATION_NOTES.md`.

## M61.3 update — consolidated Visual Graph + PathWalk workflow

M61.3 adds a stable companion utility workflow guide:

```text
source/program.ordo.yaml
  → Visual Graph Generator: visual tree inspection
  → PathWalk: graph summary, terminal paths, clean/noise cases, review cards
  → Visual Graph annotation overlay: optional reviewer notes/highlights
```

See `docs/apf/legacy-root/COMPANION_UTILITY_WORKFLOW.md` and `utilities/COMPANION_UTILITY_WORKFLOW.md`.

M61.3 is docs-only. It does not execute generated testcases, score model behavior, calibrate weights, or merge utilities.
