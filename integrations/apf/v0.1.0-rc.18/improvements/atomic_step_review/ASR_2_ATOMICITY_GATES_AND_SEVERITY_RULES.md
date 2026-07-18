# ASR-2 — Atomicity gates and severity evaluation rules

Status: completed

ASR-2 formalizes the Atomic Step Review as ten deterministic gates with evidence-bound results and aggregation rules.

## Added gates

- `SINGLE_RESPONSIBILITY_GATE`
- `SINGLE_OUTPUT_GATE`
- `EXPLICIT_INPUT_OUTPUT_GATE`
- `NO_HIDDEN_RECONSTRUCTION_GATE`
- `SEPARATE_GENERATION_VALIDATION_GATE`
- `EXPLICIT_CONFIRMATION_GATE`
- `NO_PARTIAL_SUCCESS_TRANSITION_GATE`
- `FAILURE_LOCALIZATION_GATE`
- `ARTIFACT_LEVEL_STATUS_GATE`
- `INDEPENDENT_POST_RENDER_REVIEW_GATE`

## Severity behavior

- `passed`: no violation and sufficient evidence;
- `recommendation`: safe non-blocking improvement;
- `blocking_issue`: unsafe pattern blocks progression;
- `needs_human_decision`: progression pauses because a business or authority boundary is unresolved.

A blocking issue cannot be silently downgraded. Human authority may choose between valid decompositions, but cannot waive missing evidence, hidden reconstruction, partial-success transition, or required validation.

No Ordo core changes or internal APF runtime enforcement were introduced.
