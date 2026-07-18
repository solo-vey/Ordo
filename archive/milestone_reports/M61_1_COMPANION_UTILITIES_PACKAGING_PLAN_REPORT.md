# M61.1 — Companion Utilities Packaging Plan Report

Status: **passed-design-docs-only**.

## Base

M61.1 starts from **M61.0 Human Review Scenario Cards**.

## Scope completed

- Added `COMPANION_UTILITIES.md`.
- Added `utilities/README.md`.
- Added `utilities/VISUAL_GRAPH_GENERATOR_INTEGRATION_PLAN.md`.
- Updated package index/backlog wording for the companion utility layer.
- Added a book chapter on companion utilities.
- Documented PathWalk as the included testcase/review artifact utility.
- Documented Visual Graph Generator as an evaluated external candidate planned for M61.2 import.

## Visual Graph Generator candidate reviewed

Candidate archive:

```text
ordo_visual_graph_generator_v1_1_annotation_preview.zip
```

Observed candidate capabilities:

- Ordo YAML/IR to `.mmd`, `.svg`, `.png`;
- full graph, subtree, context view, path-only view;
- branch labels, gates, terminal paths, terminal artifacts, package/archive outputs;
- annotation overlay and trace overlay contracts;
- read-only structural visualization role.

## Explicit non-scope

M61.1 did not:

- import Visual Graph Generator code;
- refactor PathWalk;
- change Ordo runtime-core semantics;
- change scoring weights;
- run model/API benchmarks;
- reopen runtime-harness or transcript-replay matrix gates.

## Future backlog update

M61.2 is reserved for **Visual Graph Generator Package Import**.  
M61.3 may consolidate combined utility documentation.  
M62.0 remains the future runtime execution milestone for generated testcases.

## Validation summary

M61.1 is docs/design-only. Validation used syntax/docs/package integrity gates and lightweight existing utility smokes, not runtime execution gates.

Passed checks:

- workspace `py_compile`: passed;
- selected non-runtime PathWalk pytest: `20 passed`;
- workspace graph → paths → clean-cases → noise-cases → review-cards smoke: passed, `15` cards;
- PathWalk RC `py_compile`: passed;
- PathWalk RC + developer bundle smoke: passed, `15` cards;
- external Visual Graph Generator `py_compile`: passed;
- external Visual Graph Generator pytest: `12 passed`;
- external Visual Graph Generator `.mmd` smoke: passed;
- external Visual Graph Generator `.svg` smoke: passed.

Runtime-harness/transcript-replay matrix gates were intentionally not used.
