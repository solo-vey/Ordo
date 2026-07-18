# Future Backlog after M62 Line Closure

Completed:

- M62.0 — APF Integration Correlation Plan.
- M62.1 — APF Package Import into Current Language Package.
- M62.2 — APF Documentation and Book Section.
- M62.3 — APF Language Pattern Extraction Plan.
- M62 Line Closure — stable APF integration boundary.

Recommended next line:

- M63.0 — APF Branch Review Continuation Plan.

M63 should start from the APF improvement-package paused point:

```text
branch: 1. Доменна модель + дерево рішень
current_node: Node review
```

Still future work:

- close APF branch 1 and branch 2 review;
- apply scoped APF YAML patch only after review closure;
- implement terminal output binding / template verification loop;
- implement progressive tree authoring patch;
- adapt APF cyclic review graph for PathWalk terminal-path/case generation if needed;
- design `FLOW.JOIN` / `SHARED.TAIL.REFERENCE` formally before IR/compiler changes;
- runtime execution/scoring/calibration remains deferred;
- watchdog/process-boundary hardening remains separate infrastructure work.

---

# Future Backlog after M62.2

Completed:

- M62.0 — APF Integration Correlation Plan.
- M62.1 — APF Package Import into Current Language Package.
- M62.2 — APF Documentation and Book Section.

Next recommended:

- M62.3 — APF Language Pattern Extraction Plan.

Still future work:

- APF branch 1/2 scoped corrections after review closure.
- Terminal output binding implementation patch.
- Progressive tree authoring APF patch.
- Formal promotion of APF pattern candidates only after classification.
- Runtime execution/scoring/calibration remains future work and should not be reopened as a small patch.
- Watchdog/process-boundary hardening remains separate future infrastructure work.

---

# Future Backlog after M62.1

Completed:

- M62.0 — APF Integration Correlation Plan.
- M62.1 — APF Package Import into Current Language Package.

Still future work:

- M62.2 — APF Documentation and Book Section.
- M62.3 — APF Language Pattern Extraction Plan.
- APF branch 1/2 scoped corrections after review closure.
- Terminal output binding implementation patch.
- Formal promotion of APF pattern candidates only after classification.
- Runtime execution/scoring/calibration remains future work and should not be reopened as a small patch.

---

# M62.0 — APF Integration Correlation Plan

M62.0 starts the Applied Project Factory integration line after M61 Companion Utilities Line Closure. It is docs/design-only: APF is correlated and classified as a future standard applied module import target, but APF code is not imported yet.

Start here:

- `APF_INTEGRATION_CORRELATION_PLAN.md`
- `STANDARD_APPLIED_MODULES.md`
- `APF_LANGUAGE_PATTERN_CANDIDATES.md`
- `M62_0_APF_INTEGRATION_CORRELATION_PLAN_REPORT.md`

Next planned milestone: `M62.1 — APF Package Import into Current Language Package`.

---

# M61 Line Closure

M61 is closed as the stable companion-utility line. Use the M61 Line Closure archives for handoff when the user needs the complete Visual Graph + PathWalk workflow. Runtime execution, scoring, calibration, and additional noise variants remain future work.

See `M61_LINE_CLOSURE_REPORT.md` and `M61_COMPANION_UTILITIES_LINE_CLOSURE.md`.

---

# Future Backlog after M61.1

### M61.1 — Companion Utilities Packaging Plan

Status: completed as design/docs-only. It defines the companion utility layer and records Visual Graph Generator as a planned M61.2 import.

### M61.2 — Visual Graph Generator Package Import

Planned: import the external Visual Graph Generator under `utilities/ordo_visual_graph_generator/` with minimal refactor, preserve its tests/examples/docs, and keep it outside runtime core.

### M61.3 — Utility Documentation Consolidation

Planned: combined quickstarts for Visual Graph Generator + PathWalk.

### M62.0 — Runtime Execution of Generated Testcases

Still future work. Keep separate because it can reopen process-boundary/watchdog risks.

---

# Future Backlog after M61.0

## Completed from earlier backlog

### M61.0 — Human Review Scenario Cards

Implemented as artifact-only review-card generation. It converts clean/noise testcase summaries into QA/developer scenario cards and intentionally does not run runtime, score behavior, or calibrate weights.


This backlog records useful directions that remain after M61.0. They are not current blockers.

## M62.0 — Runtime Execution of Generated Testcases

Purpose: execute generated real-module testcases against runtime packages and collect evidence.

Prerequisites:

- explicit process-boundary design;
- hard timeout/watchdog for every child runtime invocation;
- no long-lived parent-loop blocking on embedded runtime calls;
- collect-only behavior for completed jobs;
- clear non-goals around scoring/calibration until raw evidence is stable.

Risks:

- this may reopen the M60.6.5 / M60.6.4.1 blocked area;
- it should not be started as a small patch unless the milestone explicitly owns watchdog/process-boundary hardening.

## Deferred noise patterns

The following patterns remain future improvements:

- `backtrack`;
- `correction_backtrack`.

They are valuable but should be added only when there is a clear consumer for them, such as scenario cards or runtime execution, not as endless noise expansion.


## Updated after M61.2

Completed:

- M61.2 — Visual Graph Generator Package Import.

Still future work:

- M61.3 — Utility Documentation Consolidation: combined PathWalk + Visual Graph author workflow.
- M62.0 — Runtime Execution of Generated Testcases.
- Backtrack and correction-backtrack testcase patterns.
- Watchdog/process-boundary hardening before any broad runtime execution matrix.

## M61.3 backlog status update

M61.3 closes the documentation gap between Visual Graph Generator and PathWalk by adding a combined author/reviewer workflow. The following remain future work and are not blockers for the utility documentation line:

- M62.0 runtime execution of generated testcases;
- scoring generated real-module cases;
- model/API benchmark orchestration;
- watchdog/process-boundary hardening;
- `backtrack` and `correction_backtrack` noise variants;
- optional future unified wrapper CLI for companion utilities.


## Updated after M62.3

Completed:

- M62.3 — APF Language Pattern Extraction Plan.

Still future work:

- M62 Line Closure to freeze APF import/docs/classification as a stable boundary.
- M63.0 — APF Branch Review Continuation Plan, starting from branch 1 `Node review` and then branch 2.
- APF scoped YAML patch only after branch review closure.
- Terminal output binding implementation patch.
- `FLOW.JOIN` / `SHARED.TAIL.REFERENCE` formal language/IR design milestone.
- Runtime execution/scoring/calibration remains deferred.
