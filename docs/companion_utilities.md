# M61 Line Closure

M61 is closed as the stable companion-utility line. Use the M61 Line Closure archives for handoff when the user needs the complete Visual Graph + PathWalk workflow. Runtime execution, scoring, calibration, and additional noise variants remain future work.

See `M61_LINE_CLOSURE_REPORT.md` and `M61_COMPANION_UTILITIES_LINE_CLOSURE.md`.

---

# M61.1 — Companion Utilities Packaging Plan

Status: **design/docs-only**.  
Base: **M61.0 Human Review Scenario Cards**.  
Scope: package structure, documentation, utility taxonomy, integration boundaries.  
Non-scope: importing the Visual Graph Generator code, refactoring PathWalk, runtime execution, scoring, calibration, or model/API benchmark orchestration.

## Why this layer exists

Ordo is the language/runtime layer. Companion utilities are optional tools that help authors, reviewers, and developers inspect, test, and explain Ordo programs without becoming part of the runtime core.

The utility layer should stay explicit because different tools answer different questions:

| Question | Utility |
|---|---|
| What does this Ordo YAML tree look like? | Visual Graph Generator |
| What terminal paths exist in this real module? | PathWalk |
| What clean-path and bounded-noise testcases should reviewers inspect? | PathWalk |
| What scenario cards can a human QA/reviewer read? | PathWalk |
| Did the runtime execute a session correctly? | Runtime / future execution harness, not this layer |

## Current companion utilities

### 1. PathWalk

Current status: **included and stable as a companion utility**.

Package location today:

```text
ordo_pathwalk/
```

Primary M60.7/M61.0 artifact-only workflow:

```text
source/program.ordo.yaml
  → real-module-graph
  → real-module-paths
  → real-module-clean-cases
  → real-module-noise-cases
  → real-module-review-cards
```

Representative CLI:

```bash
PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-graph   --source source/program.ordo.yaml   --out runs/real_module_graph   --force

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-paths   --summary runs/real_module_graph/REAL_MODULE_GRAPH_SUMMARY.json   --out runs/real_module_paths   --force

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-clean-cases   --paths runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json   --out runs/real_module_clean_cases   --force

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-noise-cases   --paths runs/real_module_paths/REAL_MODULE_TERMINAL_PATHS.json   --out runs/real_module_noise_cases   --force

PYTHONPATH=cli:. python3 -m ordo_pathwalk.cli real-module-review-cards   --clean-summary runs/real_module_clean_cases/SUMMARY.json   --noise-summary runs/real_module_noise_cases/SUMMARY.json   --out runs/real_module_review_cards   --force
```

PathWalk is a testcase/review artifact generator. It must not be treated as Ordo runtime core.

### 2. Visual Graph Generator

Current status: **evaluated external utility candidate; not imported in M61.1**.

Source archive inspected for M61.1:

```text
ordo_visual_graph_generator_v1_1_annotation_preview.zip
```

Observed top-level candidate files:

```text
README.md
ORDO_GRAPH_INPUT_CONTRACT.md
GRAPH_OUTPUT_LAYERS.md
ANNOTATION_OVERLAY_SCHEMA.md
TRACE_OVERLAY_SCHEMA.md
ordo_graph.py
ordo_graph_annotation_demo.py
ordo_graph_with_attached_gates.py
examples/
reference_outputs/
tests/
```

Observed capabilities:

- render Ordo YAML/IR into Mermaid `.mmd`;
- render Graphviz-backed `.svg` and `.png` when `dot` is installed;
- render full graph, subtree, context view, and path-only view;
- show branch labels, gates, terminal/repair/error paths, terminal artifacts, and package/archive outputs;
- support annotation overlays and trace overlay schemas;
- remain read-only: no runtime execution, no LLM/MCP call, no YAML mutation, no business-semantic validation claim.

Recommended M61.2 import location:

```text
utilities/
  ordo_visual_graph_generator/
    README.md
    ORDO_GRAPH_INPUT_CONTRACT.md
    GRAPH_OUTPUT_LAYERS.md
    ANNOTATION_OVERLAY_SCHEMA.md
    TRACE_OVERLAY_SCHEMA.md
    ordo_graph.py
    ordo_graph_annotation_demo.py
    ordo_graph_with_attached_gates.py
    examples/
    tests/
```

This preserves the working standalone utility first. A later milestone may add a normalized wrapper package if needed.

## Utility taxonomy

| Layer | Included in runtime core? | Mutates source? | Executes sessions? | Primary output |
|---|---:|---:|---:|---|
| Ordo runtime / CLI | Yes | No, except generated runtime/session artifacts | Yes | Runtime artifacts, session trace |
| PathWalk | No | No | No for M60.7/M61.0 artifact-only line | Graph summaries, paths, testcases, review cards |
| Visual Graph Generator | No | No | No | `.mmd`, `.svg`, `.png`, overlay reports |

## Integration phases

### M61.1 — Companion Utilities Packaging Plan

Accepted scope:

- define the companion utility layer;
- document PathWalk and Visual Graph Generator responsibilities;
- create a stable package layout proposal;
- update stable package/backlog documentation;
- add a book chapter for companion utilities.

### M61.2 — Visual Graph Generator Package Import

Planned scope:

- import the utility under `utilities/ordo_visual_graph_generator/` without heavy refactor;
- preserve its existing README, contracts, examples, and tests;
- add package-level integration README;
- run `py_compile`, existing pytest, Mermaid smoke, and SVG smoke when Graphviz `dot` is available;
- do not make it part of runtime core.

### M61.3 — Utility Documentation Consolidation

Planned scope:

- add combined quickstarts for PathWalk + Visual Graph Generator;
- document when to use graph visualization before testcase/review-card generation;
- add examples showing the author workflow:

```text
source/program.ordo.yaml
  → Visual Graph: inspect tree
  → PathWalk: enumerate paths and generate cases/cards
  → Visual Graph annotation overlay: highlight review/debug notes
```

### M62.0 — Runtime Execution of Generated Testcases

Future milestone only. This is intentionally separate because it may reopen process-boundary/watchdog risks from the blocked M60.6.5/M60.6.4.1 branch.

## Non-goals and guardrails

The companion utility layer must not:

- hide runtime-core changes inside utility changes;
- make generated graphs or cards claim runtime validation;
- use runtime-harness/matrix tests as a docs-only milestone gate;
- calibrate scoring weights;
- execute generated testcases until a dedicated execution milestone exists;
- refactor a working external utility during its first import without a reason.

## Stable handoff wording

Use this wording in package documentation:

```text
Ordo companion utilities are optional developer/reviewer tools shipped beside the language package. They do not define runtime semantics. PathWalk generates testcase and review artifacts. Visual Graph Generator renders Ordo YAML/IR as visual graphs for inspection, explanation, and debugging.
```

## M61.1 decision

M61.1 approves the utility-layer packaging plan and defers code import of Visual Graph Generator to M61.2.
