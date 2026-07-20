# M62.2 — APF Documentation and Book Section

M62.2 documents `ordo.applied_project_factory` as a standard applied module and explains the APF + Visual Graph + PathWalk review route.

Start here:

- `docs/apf/legacy-root/APF_STANDARD_MODULE_GUIDE.md`
- `docs/apf/legacy-root/APF_COMPANION_WORKFLOW.md`
- `docs/apf/legacy-root/STANDARD_APPLIED_MODULES.md`
- `packages/ordo_applied_project_factory/docs/APF_STANDARD_MODULE_GUIDE.md`
- `M62_2_APF_DOCUMENTATION_AND_BOOK_SECTION_REPORT.md`

M62.2 is documentation-only: no APF branch rewrite, no runtime-core changes, no IR/opcode additions, and no runtime execution/scoring.

---

# M62.1 — APF Package Import

M62.1 imports `ordo.applied_project_factory` v0.1.0-alpha.14 as a standard applied module in the current language package.

Use M62.1 archives when the developer needs the current language package with:

```text
language core
companion utilities: PathWalk + Visual Graph Generator
standard applied modules: history_event_guided_intake, ordo_project_builder, ordo_hybrid_executor, ordo_applied_project_factory
```

Start here:

- `docs/apf/legacy-root/APF_PACKAGE_IMPORT.md`
- `docs/apf/legacy-root/STANDARD_APPLIED_MODULES.md`
- `packages/ordo_applied_project_factory/ORDO_PARENT_PACKAGE_IMPORT.md`
- `M62_1_APF_PACKAGE_IMPORT_REPORT.md`

M62.1 does not rewrite APF branch logic or formalize APF pattern candidates as IR/opcodes.

---

# M62.0 — APF Integration Correlation Plan

M62.0 starts the Applied Project Factory integration line after M61 Companion Utilities Line Closure. It is docs/design-only: APF is correlated and classified as a future standard applied module import target, but APF code is not imported yet.

Start here:

- `docs/apf/legacy-root/APF_INTEGRATION_CORRELATION_PLAN.md`
- `docs/apf/legacy-root/STANDARD_APPLIED_MODULES.md`
- `docs/apf/legacy-root/APF_LANGUAGE_PATTERN_CANDIDATES.md`
- `M62_0_APF_INTEGRATION_CORRELATION_PLAN_REPORT.md`

Next planned milestone: `M62.1 — APF Package Import into Current Language Package`.

---

# M61 Line Closure

M61 is closed as the stable companion-utility line. Use the M61 Line Closure archives for handoff when the user needs the complete Visual Graph + PathWalk workflow. Runtime execution, scoring, calibration, and additional noise variants remain future work.

See `M61_LINE_CLOSURE_REPORT.md` and `M61_COMPANION_UTILITIES_LINE_CLOSURE.md`.

---

# M61.1 Stable Package Index Note

M61.1 preserves the M61.0 code base and adds docs for the companion utility layer. The package still uses PathWalk as the included testcase/review artifact utility. Visual Graph Generator is documented as a planned M61.2 import and is not yet copied into the stable package.

Use:

- Workspace archive for full developer handoff and docs.
- Developer Bundle for runtime/CLI + docs handoff.
- PathWalk RC for standalone PathWalk artifact-only review workflows.

Do not treat Visual Graph Generator as included until M61.2 or later.

---

# M60.8 Stable Package Index

Use the newest M60.8 archives as the canonical handoff package set.

## Primary package

- Workspace archive: full development workspace, tests, docs, packages, PathWalk, reports.
- Developer bundle: smaller handoff bundle for language/CLI/package usage.
- PathWalk RC: standalone companion utility release candidate.
- Book source: markdown source only; no PDF generated in M60.8.

## Stable base rule

```text
Use M60.8 archives for handoff.
Use M60.7.5 semantics for real-module artifact generation.
Use M60.6.4 as the stable transcript-replay pilot reference.
Do not base future work on M60.6.5 or M60.6.4.1 WIP/blocker experiments.
```

## Quick package choice

| Need | Use |
|---|---|
| Continue development | workspace archive |
| Use CLI/language/package docs | developer bundle |
| Run PathWalk artifact-only tools beside a developer bundle | PathWalk RC |
| Update the book source later | book source archive |
| Inspect evidence for this consolidation | M60.8 evidence zip |

## Scope boundary

M60.8 is docs-only consolidation. It should not be interpreted as a new runtime or benchmark milestone.

## M61.0 package note

For review-oriented QA handoff, use the newest M61.0 archives. They preserve the M60.8 stable handoff boundary and add `real-module-review-cards` as an artifact-only PathWalk feature.


## M61.2 — Visual Graph Generator Package Import

Current companion utilities:

```text
ordo_pathwalk/
utilities/ordo_visual_graph_generator/
```

M61.2 imports Visual Graph Generator as a read-only utility for Mermaid/SVG/PNG graph rendering and annotation overlays. The stable developer route remains artifact-only for utilities: visualization and review artifacts are allowed; runtime execution/scoring remains future work.

## M61.3 — Utility Documentation Consolidation

Use M61.3 archives when handing the package to a developer/reviewer who needs the complete companion utility route.

Recommended route:

```text
source/program.ordo.yaml
  → utilities/ordo_visual_graph_generator/ordo_graph.py
  → ordo_pathwalk real-module-graph
  → ordo_pathwalk real-module-paths
  → ordo_pathwalk real-module-clean-cases
  → ordo_pathwalk real-module-noise-cases
  → ordo_pathwalk real-module-review-cards
```

M61.3 remains documentation consolidation only. It does not add runtime execution or scoring.


## M62.3 — APF Language Pattern Extraction Plan

Current APF integration status:

```text
M62.1: APF package imported.
M62.2: APF documentation and book section added.
M62.3: APF language/process-model candidates classified.
```

No APF YAML rewrite, IR/opcode promotion, runtime-core change, execution, scoring, or calibration is part of M62.3.
