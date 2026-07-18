# M62.3 — APF Language Pattern Extraction Plan

Status: `classification-only / no-runtime-core-change`  
Date: `2026-07-08`  
Base: `M62.2 — APF Documentation and Book Section`

## Purpose

M62.3 classifies the language/process-model improvements discovered during APF `v0.1.0-alpha.14` review. It does **not** rewrite APF branch logic, promote new opcodes, change IR semantics, or execute generated testcases.

The goal is to avoid turning the APF improvement package into one large uncontrolled language rewrite. Every candidate is assigned to an initial home:

```text
Documentation pattern
APF reusable subflow
Schema convention
Artifact standard
Rendering standard
Package authoring policy
Lint candidate
Future IR candidate
```

## Promotion ladder

A candidate must move through evidence stages before it can become runtime or IR:

```text
observed APF need
→ documented APF pattern
→ reusable APF subflow / state convention
→ used by more than one package
→ lint/check candidate
→ formal language construct
→ IR/runtime object only when necessary
```

M62.3 stops at classification. No candidate is promoted directly to opcode/IR.

## Classification counts

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

## High-priority conclusions

### Immediate documentation / authoring standards

These can be documented now because they clarify how APF and future authoring modules should behave:

- `PROCESS.AUTHORING.RUNTIME`
- `TREE.AUTHOR.PROGRESSIVE`
- `CURRENT.NODE.DISPLAY.BLOCK`
- `YAML.PATCH.SCOPED`
- `VALIDATION.MINIMAL`
- `VALIDATION.FULL.DEFERRED`
- `TECHNICAL/HUMAN/HANDOFF STATUS SPLIT`

### APF patch candidates, but not M62.3 implementation

These should drive the future APF scoped patch after branch 1 / branch 2 review closure:

- `INPUT.POLICY`
- `OUTPUT.CANDIDATE.CATALOG`
- `TREE.VISION.CAPTURE`
- `SUBTREE.DRAFT`
- `NODE.REVIEW`
- `BRANCH.REVIEW`
- `NODE.NEXT_STEP.DECISION`
- `TERMINAL.OUTPUT.SELECT`
- `TERMINAL.OUTPUT.BIND`
- `OUTPUT.TEMPLATE.CHECK`
- `OUTPUT.MOCK.EXAMPLE`
- `TERMINAL.READY.CHECK`
- `CONTROL.ACTION.BOOKKEEPING`

### Future language / IR candidates

These are valuable, but must not be rushed:

- `FLOW.JOIN`
- `SHARED.TAIL.REFERENCE`

Reason: they may need compiler/IR semantics because shared-tail duplication is a structural modeling issue. But they need a dedicated design milestone, not a side effect of APF import.

## Candidate classification matrix

| candidate | classification | priority | current_home | future_home | m62_3_decision |
| --- | --- | --- | --- | --- | --- |
| PROCESS.AUTHORING.RUNTIME | documentation_pattern | P0 | APF standard module docs + book | language/process-model guide | Document as the parent pattern; do not promote to runtime core. |
| INPUT.POLICY | schema_convention | P0 | APF state/schema convention | language package authoring standard; possible lint candidate | Formalize first as state/schema convention, not opcode. |
| OUTPUT.CANDIDATE.CATALOG | schema_convention | P0 | APF output planning convention | standard module authoring schema | Keep as candidate catalog model until several modules use it. |
| TERMINAL.OUTPUT.SELECT | apf_reusable_subflow | P0 | APF terminal output binding loop | reusable applied-module subflow; possible authoring DSL pattern | Treat as APF subflow before formal language construct. |
| TERMINAL.OUTPUT.BIND | apf_reusable_subflow | P0 | APF terminal path review | standard terminal-output binding pattern | Document as reusable subflow; defer opcode/IR promotion. |
| OUTPUT.TEMPLATE.CHECK | apf_reusable_subflow | P0 | APF template review loop | possible lint/check rule after APF patch | Plan as APF subflow; only later evaluate lint rule. |
| OUTPUT.TEMPLATE.DRAFT | apf_reusable_subflow | P1 | APF output artifact creation loop | template authoring guide | Keep APF-local until template lifecycle stabilizes. |
| OUTPUT.MOCK.EXAMPLE | artifact_standard | P0 | template review artifact standard | output template documentation standard; possible validation checklist | Adopt as documentation/artifact standard before automation. |
| OUTPUT.TEMPLATE.REVIEW | apf_reusable_subflow | P0 | APF review model | standard review decision pattern | Keep as guided APF subflow. |
| TERMINAL.READY.CHECK | lint_candidate | P0 | APF readiness checklist | lint/check candidate after APF patch | Mark as first serious future lint candidate, not active rule. |
| TREE.AUTHOR.PROGRESSIVE | documentation_pattern | P0 | APF authoring model | language process-authoring guide | Promote as documented authoring pattern, not runtime construct. |
| TREE.VISION.CAPTURE | apf_reusable_subflow | P0 | APF branch 1/2 authoring flow | process authoring module pattern | Keep APF-local until branch 1/2 review closes. |
| SUBTREE.DRAFT | apf_reusable_subflow | P0 | APF draft generation flow | authoring package standard | Keep as APF subflow with explicit draft != approved rule. |
| SUBTREE.REVIEW.START | apf_reusable_subflow | P1 | APF review loop | review workflow convention | Document as transition point in APF. |
| NODE.REVIEW | apf_reusable_subflow | P0 | APF review model | standard process-review pattern | Use as APF-level reusable subflow; do not create opcode. |
| BRANCH.REVIEW | apf_reusable_subflow | P0 | APF review model | standard process-review pattern | Use as APF-level reusable subflow. |
| NODE.NEXT_STEP.DECISION | apf_reusable_subflow | P0 | APF node review sequence | process authoring pattern | Treat as required APF patch item, not language core. |
| CURRENT.NODE.DISPLAY.BLOCK | rendering_standard | P0 | APF user-facing runtime review policy | language review-rendering standard | Promote as review rendering standard, not IR object. |
| CONTROL.ACTION.BOOKKEEPING | schema_convention | P0 | APF review state convention | review-state schema convention; possible lint checklist | Formalize in APF review state first. |
| FLOW.JOIN | future_ir_candidate | P0 | APF branch 4 pattern | language flow modeling candidate; possible compiler/lint support | Treat as highest-value future IR candidate, but not in M62.3. |
| SHARED.TAIL.REFERENCE | future_ir_candidate | P0 | APF branch 4 pattern | flow model / compiler representation candidate | Pair with FLOW.JOIN for future design. |
| YAML.PATCH.SCOPED | package_authoring_policy | P0 | APF process-correction policy | developer workflow standard | Adopt as policy/checklist, not runtime operation. |
| VALIDATION.MINIMAL | package_authoring_policy | P0 | APF correction flow | standard package lifecycle | Keep aligned with existing Ordo validation discipline. |
| VALIDATION.FULL.DEFERRED | package_authoring_policy | P0 | APF validation strategy | package lifecycle docs; possible validation profile | Document as lifecycle rule; do not enforce globally yet. |
| PROCESS.FEEDBACK.CAPTURE | apf_reusable_subflow | P1 | APF correction/improvement branch idea | process improvement workflow | Keep as future APF subflow until branch 4 evidence is broader. |
| PROCESS.CHANGE.PROPOSE | apf_reusable_subflow | P1 | APF existing process improvement flow | standard improvement workflow | Keep paired with PROCESS.FEEDBACK.CAPTURE. |
| PROCESS.CHANGE.APPLY | apf_reusable_subflow | P1 | APF correction flow | standard improvement workflow / patch lifecycle | Keep APF-local until scoped patch representation is stable. |
| GRAPH.SVG.POLICY | documentation_pattern | P1 | APF docs + Visual Graph docs | companion utility workflow standard | Document only; already supported by Visual Graph utility. |
| TECHNICAL/HUMAN/HANDOFF STATUS SPLIT | schema_convention | P0 | APF status model | package lifecycle status convention; possible docs/lint support | Formalize as status vocabulary in docs first. |

## Non-goals

M62.3 does not:

- modify `packages/ordo_applied_project_factory/source/program.ordo.yaml`;
- close APF branch 1 or branch 2 review;
- implement terminal output binding;
- add APF lint rules;
- add new IR/opcode objects;
- change runtime core;
- run runtime execution/scoring/calibration;
- reopen watchdog/process-boundary hardening.

## Recommended next boundary

M62.3 is a good closure point for the APF integration/documentation/extraction line. The next safe move is either:

1. **M62 Line Closure** — freeze APF import + documentation + classification as a stable handoff point; or
2. **M63.0 — APF Branch Review Continuation Plan** — return to APF branch 1 `Node review`, then branch 2, and only after review closure plan a scoped YAML patch.

Do not start `FLOW.JOIN`/IR implementation or terminal-output-binding patch as a small follow-up. Those are larger milestones.
