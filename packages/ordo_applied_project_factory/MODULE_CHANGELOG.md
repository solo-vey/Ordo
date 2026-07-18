# Module Changelog — ordo.applied_project_factory

## v0.1.0-rc.1 — M62 release-candidate adaptation

- Promotes APF `0.1.0-alpha.21` to release-candidate status on the current M62 language package.
- Preserves the closed APF authoring process logic from alpha.21.
- Keeps M62 language-pattern classifications intact: APF patterns remain documentation/subflow/schema conventions, not runtime core opcodes.
- Updates standard-applied-module metadata, version docs, state fixture, and validation profile for the M62 parent CLI.
- Adds RC validation report and package artifacts.


---


## 0.1.0-alpha.21 — full validation readiness technical patch

- Aligns package manifest/version metadata with 0.1.0-alpha.21.
- Adds missing static coverage tests for alpha.18-alpha.20 shared subflows and integration gates.
- Adds deterministic contract coverage appendices to required docs/templates.
- Adds `run_inputs/alpha21_full_validation_state.yaml` as the full-validation state fixture.
- Does not change approved APF process logic.

# Module Changelog

## 0.1.0-alpha.18 — shared output/template subflow closure

- Closed the shared terminal output/template subflow after human UX review.
- Terminal output policy selection now has explicit branches for existing output, new artifact, no output, and deferred output decision.
- New artifact creation now starts from free-form user intent after showing available terminal state fields; fixed artifact-type lists are hints only, not constraints.
- Output recipes now capture direct-insert fields, generated sections, generation instructions, and required state fields.
- Document-like artifacts default to file-first review packages with downloadable template, mock-filled example, mapping report, and assumptions/risks summary.
- User review actions are simplified to four decisions: confirm, revise, defer, or remove artifact.
- Deferred templates are recorded as unfinished; final gates block artifact use until the template is completed or the artifact is removed from the terminal point.
- Added terminal output binding confirmation and terminal path readiness checks that reject unfinished active artifacts/templates.

## 0.1.0-alpha.17 — branch 2 manual-tree entry adapter

- Closed Branch 2 as a short entry adapter rather than a separate full process.
- Manual-tree authoring now captures user-supplied trees in human formats: outline, if/then logic, table, Mermaid-like sketch, pseudocode, root+branches, subtree, or full draft.
- Added normalization into `normalized_tree_draft` with aliases, labels, branch conditions, terminal candidates, missing branches, ambiguous transitions, implied gates, possible outputs, and open questions.
- Added completeness/join logic: structured trees join `N_DRAFT_SUBTREE_REVIEW_START`; partial/sketch trees join `N_DRAFT_SUBTREE_GENERATION`.
- Added assertions preventing manual input from becoming `approved_decision_tree` directly and requiring reuse of Branch 1 shared downstream path.
- Full validation/handoff remains shared and is not duplicated.

## 0.1.0-alpha.16 — free-dialogue branch consistency delta

- Closed branch 3 by delta review instead of rewalking the whole free-dialogue flow.
- Confirmed existing free-dialogue behavior: raw notes, plain-language extraction, draft tree generation, node/branch review, correction/defer/approve, sibling/deferred tracking, and shared validation-tail reuse.
- Added explicit free-dialogue extraction of candidate output artifacts, candidate template hints, and output-related open questions.
- Added output policy tolerance for free dialogue: outputs may be known, partial, AI-proposed, deferred, or absent.
- Routed terminal points from free-dialogue draft review to the shared terminal output binding + template verification loop with mock-filled examples.
- Added assertion `A_FREE_DIALOGUE_OUTPUT_CANDIDATES_NOT_DROPPED` to prevent dropping output/document/template mentions from free-dialogue notes.


## v0.1.0-alpha.15 — Branch 1 progressive authoring and output-template review

- Closed human review for branch 1: `Доменна модель + дерево рішень`.
- Moved `runtime_entry_point` after domain model, input policy, output catalog and open questions.
- Split input/output intake into separate process concepts.
- Made input artifacts policy-based: required, optional, none, unknown/deferred, or produced later.
- Separated output artifact catalog from template verification.
- Added terminal output binding: every terminal point must choose no-output, selected outputs, added output, or deferred output.
- Added template verification with mock-filled examples before terminal path readiness.
- Replaced static decision-tree blueprint with progressive tree authoring: shallow root/branches, deeper subtree, full draft, or free-form logic.
- Added terminal-or-continue decision with branches for terminal, next branching, intermediate node, restructure previous logic, and deferred branch.
- Added subtree completion and approved tree consolidation before state schema/gate review/YAML generation.
- Full validation remains a shared terminal/pre-handoff gate and is not duplicated in branch 1.

## 0.1.0-alpha.14 — existing-process improvement branch

- Added the fourth startup mode: `existing_process_improvement`.
- Added baseline selection for existing-process correction: full workspace/dev package archive or self-contained `source/program.ordo.yaml` only.
- Added batch improvement flow: improvement list → candidate extraction → candidate selection → mapping → before/after affected-node review.
- Added targeted improvement flow: target identification → change clarification → before/after proposal → change decision → loop or close.
- Added shared change pipeline for existing-process correction: confirmed change set → scoped YAML patches → minimal validation.
- Connected existing-process correction to the existing terminal/pre-handoff full-validation gate without duplicating shared downstream nodes.

## 0.1.0-alpha.13 — process-design review rendering contract

- Added a durable YAML-level rendering policy for process-design review.
- Required current-node displays to label the active interaction mode: tree traversal, branch selection, node-review decision, or execution/validation gate.
- Required current-node blocks to show state, gates, artifacts/outputs/templates, pending sibling/deferred branches, and the correct decision prompt.
- Kept fourth-start-mode branch work as draft-review only; this patch does not yet commit the new existing-process-improvement branch.

## 0.1.0-alpha.13 — control-action bookkeeping separation

- Added explicit separation between real unreviewed sibling branches and not-selected runtime control actions.
- Added `selected_control_action`, `not_selected_control_actions`, `blocked_until_ready_actions`, and `control_action_decision_log` to runtime state.
- Updated node review decision gate so approve/correct/defer decisions record not-selected actions without adding them to deferred return points.
- Updated continue/approve-tree gate so `approve_tree` can be shown as blocked until required branches are reviewed.
- Minimal validation profile only: YAML parse, lint, compile/IR refresh. Full validation remains terminal/pre-handoff.

# Module Changelog

## 0.1.0-alpha.11 — incremental YAML patch cadence and terminal full-validation gate

- Added incremental YAML patch policy for tree review: after a confirmed tree step, update YAML only with a scoped patch when needed.
- Added minimal per-step validation profile: YAML parse + CLI lint + compile/IR refresh.
- Added full project validation as a terminal/pre-handoff gate instead of a per-node operation.
- Added correction loop for full-validation findings: route back to tree/YAML review rather than declaring ready.
- Added runtime state fields and gates for incremental validation cadence.

# MODULE_CHANGELOG — ordo.applied_project_factory

## 0.1.0-alpha.9 — node review Ordo-layer visibility and sibling branch tracking

- Added a confirmed node-review display contract before depth-first tree review.
- Required every current-node review to show human description, question/action, transitions, state, gates, artifacts/outputs/templates, and open/deferred branches.
- Added explicit tracking for confirmed path, current branch, unreviewed sibling branches, and deferred return points.
- Added gates and assertions preventing branch-level approval from losing sibling branches or hiding Ordo-layer metadata.
- Clarified that after confirmed process feedback the runtime must continue from reloaded YAML, not from memory of the old flow.


## 0.1.0-alpha.8 — user-facing runtime review and process feedback loop

- Disabled automatic SVG generation during node-by-node runtime review; SVG is generated only on explicit user request.
- Added required human-readable `nodes[].description` review behavior for the current-node block.
- Replaced technical alias-style extraction review with plain-language sections: what I heard, what it means, emerging tree, and open questions.
- Added process-feedback loop: accept process feedback, propose a changed step shape, ask for confirmation, update YAML, reload the updated process, and continue.
- Recorded related language-improvement proposals for `nodes[].description`, user-facing extraction summaries, and process-feedback/reload semantics.

## 0.1.0-alpha.7 — module versioning and graph annotation preview

- Switched work tracking from language-package milestone labels to module-local versioning.
- Added `module` metadata block to `source/program.ordo.yaml`.
- Added module versioning policy node, gate, contract, artifacts, and tests.
- Adopted `ordo_visual_graph_generator 1.1.0-preview` annotation overlay as an optional SVG review aid.
- Kept focused/context SVG as the default working visualization mode.

## Historical mapping

| Previous internal label | Module version |
|---|---|
| M61.1 | 0.1.0-alpha.1 |
| M61.2 | 0.1.0-alpha.2 |
| M61.3 | 0.1.0-alpha.3 |
| M61.4 | 0.1.0-alpha.4 |
| M61.5 | 0.1.0-alpha.5 |
| M61.6 | 0.1.0-alpha.6 |
| M61.6 | 0.1.0-alpha.6 |
| Module versioning + graph annotation | 0.1.0-alpha.7 |
| Current | 0.1.0-alpha.8 |


## v0.1.0-alpha.19 — Shared validation / handoff tail closure

- Closed shared validation / handoff tail as a reusable final block for all APF startup branches.
- Added explicit source YAML generation step after user approval.
- Added minimal validation step with simplified failure UX: correction or blocked defer.
- Added full validation decision: run now or skip for alpha as explicit limitation.
- Added validation result review and scoped correction loop.
- Added final unfinished-items gate before handoff package generation.
- Added file-first handoff package generation and final handoff acceptance/revision decision.
- Ensured skipped full validation is never reported as passed.
- Ensured unfinished active artifacts/templates block handoff until completed or removed.


## v0.1.0-alpha.20 — Whole-tree integration review closure

- Closed whole-tree integration review after branch and shared-tail closures.
- Verified intended joins for all four startup branches into shared output/template and validation/handoff paths.
- Added integration metadata, gates, assertions, and documentation.
- Marked legacy unreachable compatibility nodes as deprecated rather than unresolved active orphans.
- Added real structural scan report expectations for active nodes.

<!-- APF alpha.21 full-validation contract coverage appendix -->

## APF alpha.21 full-validation contract coverage appendix

This appendix records confirmed contract fields for deterministic artifact coverage validation. It is a technical release-readiness section and does not change the user-facing APF process logic.

- `previous_internal_labels`: `module.previous_internal_labels`
- `compatibility`: `module.language_compatibility`
