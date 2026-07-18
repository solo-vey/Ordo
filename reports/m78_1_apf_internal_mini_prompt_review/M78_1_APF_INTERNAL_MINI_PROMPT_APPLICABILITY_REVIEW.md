# M78.1 — APF Internal Mini-Prompt Applicability Review

## Decision

Internal mini-prompts are **not applicable to the current APF baseline**. No internal prompt is created, attached or activated.

The reviewed APF gates and runtime steps are already governed by deterministic contracts, schemas, diagnostics and enforcement. Adding prompts would duplicate authority or risk weakening fail-closed behavior.

## Reviewed objects

### PACKAGE_PROFILE_GATE
- Classification: `simple_instruction_sufficient`
- Decision: `do_not_create`
- Rationale: Package profile selection and blocking conditions are deterministic and already enforced by explicit gate and confirmation policies.

### GATE_ORDER_CONFIRMATION_GATE
- Classification: `prompt_prohibited`
- Decision: `prohibit`
- Rationale: Gate order changes require authoritative human confirmation; a mini-prompt must not influence or replace that decision.

### ATOMICITY_GATE
- Classification: `simple_instruction_sufficient`
- Decision: `do_not_create`
- Rationale: Atomicity severity, decomposition and blocking behavior are fully specified and machine validated.

### VALIDATION_REPORT_INTERPRETATION
- Classification: `simple_instruction_sufficient`
- Decision: `do_not_create`
- Rationale: Current diagnostics expose severity, path and remediation; additional prompt guidance would duplicate structured evidence.

### PACKAGE_ASSEMBLY_AND_HANDOFF
- Classification: `simple_instruction_sufficient`
- Decision: `do_not_create`
- Rationale: Assembly, checksum, clean-package and handoff requirements are deterministic and covered by release-hygiene gates.

### CSG_RUNTIME_CLASSIFICATION
- Classification: `prompt_prohibited`
- Decision: `prohibit`
- Rationale: CSG classification and state protection are runtime policy decisions; an internal mini-prompt must not override enforcement.

## Reopen conditions

- Repeatable execution variance in at least two independent replay runs.
- The issue must be residual guidance variance, not a missing contract, schema or runtime defect.
- Contract strengthening must be attempted first.
- Explicit process-owner approval is required before candidate creation.

## Closure

`BL-ORDO-009` may be closed as `review-complete-not-applicable`. Downstream playbook-authored mini-prompts remain supported and are unaffected.
