# M62.3 — APF Language Pattern Extraction Plan Report

Status: `passed-design-classification-only`  
Date: `2026-07-08`  
Base package: `M62.2 — APF Documentation and Book Section`

## Summary

M62.3 classifies APF language/process-model candidates discovered during `ordo.applied_project_factory v0.1.0-alpha.14` review. It intentionally avoids APF YAML rewrites and runtime/IR changes.

## Added artifacts

- `APF_LANGUAGE_PATTERN_EXTRACTION_PLAN.md`
- `APF_PATTERN_CLASSIFICATION_MATRIX.md`
- `APF_PATTERN_CLASSIFICATION_MATRIX.csv`
- `APF_PATTERN_CLASSIFICATION_MATRIX.json`
- `docs/apf_language_pattern_extraction_plan.md`
- `docs/apf_pattern_classification_matrix.md`
- `packages/ordo_applied_project_factory/docs/APF_LANGUAGE_PATTERN_EXTRACTION_PLAN.md`
- `packages/ordo_applied_project_factory/docs/APF_PATTERN_CLASSIFICATION_MATRIX.md`
- book chapter 67: APF language-pattern extraction

## Classification summary

| classification | count |
| --- | --- |
| apf_reusable_subflow | 14 |
| artifact_standard | 1 |
| documentation_pattern | 3 |
| future_ir_candidate | 2 |
| lint_candidate | 1 |
| package_authoring_policy | 3 |
| rendering_standard | 1 |
| schema_convention | 4 |

## Key decisions

- `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` are the strongest future IR candidates, but are not implemented in M62.3.
- `TERMINAL.READY.CHECK` is a future lint/check candidate, but blocked until APF terminal-output metadata is implemented.
- `INPUT.POLICY`, `OUTPUT.CANDIDATE.CATALOG`, `CONTROL.ACTION.BOOKKEEPING`, and status split are schema conventions first.
- `TREE.AUTHOR.PROGRESSIVE`, `NODE.REVIEW`, `BRANCH.REVIEW`, and terminal-output binding remain APF reusable subflows for future patch planning.
- Runtime execution/scoring/calibration remains out of scope.

## Non-goals confirmed

M62.3 did not:

- modify APF `source/program.ordo.yaml`;
- rewrite APF branch logic;
- promote new opcodes or IR objects;
- change runtime core;
- run runtime execution/scoring/calibration;
- reopen watchdog/process-boundary hardening;
- attempt PathWalk terminal-path enumeration through APF review-loop cycles.

## Validation summary

- Workspace `py_compile`: passed.
- Selected PathWalk + Visual Graph tests: passed.
- APF current CLI lint/compile/test: passed.
- Visual Graph APF `.mmd` smoke: passed.
- PathWalk APF `real-module-graph`: passed.
- Book manifest sanity: passed.
- Zip extraction/content checks: passed.
- Zip integrity/extraction checks: passed for final artifacts.

## Recommended next step

Recommended: `M62 Line Closure` to freeze APF import + documentation + classification as the stable boundary.

After closure, open a separate M63 line only if we are ready to continue APF branch review and plan scoped YAML patches.
