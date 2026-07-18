# 024. Artifact-Specific Rules

**Version:** 0.8.0  
**Backlog:** BL-BENCH-024  
**Status:** implemented

## Passport — DQC-PASSPORT-1

Required outcomes:

- canonical behavior, scope and out-of-scope are explicit;
- inputs, outputs, validation, mapping and terminal behavior are testable;
- positive, negative, no-op and blocked behavior are represented where relevant;
- canonical test IDs and traceability are coherent;
- assumptions and open questions are visible;
- observability expectations are defined.

The Passport is the source of truth and must not rely on Jira for missing contract behavior.

## Jira — DQC-JIRA-1

Jira is a role-aware delivery view, not a duplicate of the Passport.

Mandatory rules:

- unit-test details are not mandatory in Jira;
- references to Passport are allowed and expected where useful;
- Jira must not repeat the full Passport;
- section order and physical block location are not scored;
- required blocks may appear anywhere if clearly identifiable;
- Jira must contain scope, delivery requirements, acceptance criteria, dependencies/blockers where applicable, and traceability to the canonical contract;
- acceptance criteria must be verifiable and must not introduce behavior absent from the Passport;
- lifecycle/delivery checklist is required only when the task lifecycle warrants it.

A Jira artifact is not penalized merely because detailed payloads, test fixtures or unit-test cases remain in the Passport or QA/Automation views.

## Implementation Prompt — DQC-IMPL-PROMPT-1

Required outcomes:

- references the canonical contract;
- defines implementation scope and out-of-scope;
- requires code discovery and preservation of existing architecture;
- prohibits invented paths/symbols unless verified;
- defines implementation, verification and documentation expectations;
- includes self-check and expected impact classification;
- does not add new business behavior.

## Manual QA — DQC-MANUAL-QA-1

Manual QA must be executable for the intended tester:

- concrete input or an explicit environment-resolved placeholder;
- concrete action/request;
- expected output or expected absence;
- pass/fail assertions;
- observability path for skip/no-op/error distinction;
- canonical test-ID traceability.

Tool-neutral and environment-neutral presentation is preferred unless the environment is confirmed.

## Automation — DQC-AUTOMATION-1

Automation must be runner-oriented:

- canonical scenario/test IDs;
- fixture/setup and cleanup contract;
- invocation contract;
- assertions and negative assertions;
- expected terminal/status behavior;
- deterministic data and evidence outputs;
- feasibility/status must be honest (`specified`, `implemented`, `blocked`, etc.).

Automation source specifications and generated run reports must remain separated.
