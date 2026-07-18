# Blind Automation Validation Profile

A package passes only when all mandatory checks for its declared profile pass.

## Common checks

- execution profile is `step_bound` or `semantic_adaptive`;
- self-scoring is prohibited;
- hidden facts are not embedded in execution-model instructions;
- Driver actions and terminal states use the canonical vocabulary;
- facts use the canonical lifecycle;
- artifact versions are immutable and approvals are version-scoped;
- correction rules invalidate dependent artifact versions and approvals;
- independent evaluation separates process and document quality;
- diagnostic claims require corroboration status;
- clean-context rerun and regression comparison are required after a change.

## `step_bound` checks

- step IDs are unique and ordered;
- every mandatory step has a disclosure binding;
- transitions reference known steps;
- correction targets reference known steps;
- future-step disclosure is forbidden.

## `semantic_adaptive` checks

- intent IDs are unique;
- compound-intent behavior is explicit;
- unknown and ambiguous question behavior is explicit;
- disclosure mode is `minimal_relevant`;
- an over-disclosure guard is enabled;
- no hidden step-order inference is required.

## Fail-closed conditions

Validation fails when a package allows self-scoring, approval inheritance across versions, completion with stale artifacts, disclosure of unrequested hidden facts, a diagnostic claim without evidence status, or a terminal state outside the canonical set.
