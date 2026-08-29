# M61 Line Closure

M61 is closed as the stable companion-utility line. Use the M61 Line Closure archives for handoff when the user needs the complete Visual Graph + PathWalk workflow. Runtime execution, scoring, calibration, and additional noise variants remain future work.

See `M61_LINE_CLOSURE_REPORT.md` and `M61_COMPANION_UTILITIES_LINE_CLOSURE.md`.

---

# Ordo Companion Utilities

This directory contains optional utilities that ship beside Ordo but do not define Ordo runtime semantics.

## Current status

The Visual Graph Generator was retired from the active utility set in the 0.1.2
maintenance line. Its source and historical outputs remain under
`archive/legacy_utilities/ordo_visual_graph_generator/` for provenance.

## Utilities

| Utility | Package location | Purpose | Status |
|---|---|---|---|
| PathWalk | `utilities/ordo_pathwalk/` | Real-module graph summaries, terminal paths, clean/noise testcase artifacts, human review cards | Included |
| Playbook Lifecycle | `utilities/playbook_lifecycle/` | Upgrade-impact review, release comparison, and verified rollback checkpoints | Included |
| Playbook Regression Harness | `utilities/playbook_regression_harness/` | Versioned deterministic, semantic, stability, provenance, and behavioral-package preparation for playbook regression | Candidate 1.7.0 |
| Ordo Tree Editor | `utilities/ordo_tree_editor/` | Local browser-based visual inspection, validation, and controlled authoring of Ordo YAML graphs | Alpha v0.2.0-alpha.20.0.195-dev |

## Rule

Utilities may read Ordo YAML/IR and generate review, debug, test, or visual artifacts. They must not silently change runtime-core behavior.

## M61.3 update — consolidated Visual Graph + PathWalk workflow

M61.3 adds a stable companion utility workflow guide:

```text
source/program.ordo.yaml
  → PathWalk: graph summary, terminal paths, clean/noise cases, review cards
```

See `docs/apf/legacy-root/COMPANION_UTILITY_WORKFLOW.md` and `utilities/COMPANION_UTILITY_WORKFLOW.md`.

M61.3 is docs-only. It does not execute generated testcases, score model behavior, calibrate weights, or merge utilities.
