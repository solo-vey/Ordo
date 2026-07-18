# Chapter 81. Deterministic ARF Runtime Control Model

## Purpose

ARF-generated playbooks are executable contracts, not advisory prose. Their runtime must know which mode is active, which node is active, which actions are allowed, which evidence is authoritative, and what blocks progress.

## Default control profile

A strict working playbook declares:

```yaml
runtime_control:
  runtime_mode: PROCESS_EXECUTOR_ONLY
  decision_model: closed_world
  default_role: executor
  undefined_action: blocked_missing_instruction
```

Closed-world execution means that an action is permitted only when the active contract explicitly allows it.

## Mutually exclusive modes

ARF uses three explicit modes:

### `EXECUTION_MODE`

Execute the active node contract without redesigning the process or mutating the playbook.

### `DESIGN_MODE`

Discuss and propose changes. Repository, package, and runtime mutation are forbidden.

### `AUTHORIZED_MAINTENANCE_MODE`

Change the playbook or factory only after explicit user authorization and only within the authorized scope.

A mode change is itself an explicit governed transition. Conversation drift or a helpful suggestion cannot switch modes.

## Instruction precedence

The effective instruction order is:

```text
confirmed user decision
→ active node contract
→ authoritative node inputs
→ confirmed process state
→ authorization state
```

A lower level cannot weaken or override a higher level. Conflicting instructions at the same level produce `blocked_ambiguous_instruction`. Missing authoritative instructions produce `blocked_missing_instruction`. Execution mode does not permit invented or custom criteria.

## Runtime enforcement

Before executing an action, the runtime checks:

1. current mode;
2. active node profile;
3. prerequisites;
4. allowed inputs;
5. allowed and forbidden actions;
6. exact authorization scope;
7. explicit destination transition;
8. required validation and evidence.

Failure is fail-closed. The runtime does not substitute best judgement.

## Independent validation

Artifact production and artifact validation are separate responsibilities. A producer cannot self-declare success. Validation results are bound to the target identifier, revision, hash, and validation contract. Composite outputs are validated at mandatory atomic-unit level.

## State and invalidation

Confirmations, validations, and authorizations are revision-bound evidence. When an upstream source changes, dependent downstream evidence is invalidated. Completion status is determined by the weakest mandatory gate, not by the most optimistic label.

## Relationship to anti-patterns

These rules enforce existing fundamental anti-pattern classes, especially:

- `CONTROL_FLOW_INTEGRITY_VIOLATION`;
- `AUTHORIZATION_BOUNDARY_VIOLATION`;
- `RESPONSIBILITY_CONFLATION`;
- `STATUS_EVIDENCE_MISMATCH`;
- `STATE_COHERENCE_VIOLATION`;
- `POLICY_ENFORCEMENT_GAP`.

They do not introduce new fundamental anti-patterns.

## Practical outcome

The model remains useful for reasoning and discussion, but execution remains governed. It always has an explicit active node and mode, and it cannot silently skip, merge, redesign, validate, authorize, or complete work outside the declared contract.
