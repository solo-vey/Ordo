# CSG-3 — Response and State-Protection Rules

**Status:** normative integration artifact  
**Parent contract:** `ORDO-CAP-CSG-001`

## 1. Rule

Scope-guard responses MUST be generated from an explicit response action and MUST preserve protected process state.

Canonical operations:

```text
DEVIATION.HANDLE
STATE.PROTECT
PROCESS.PAUSE
PROCESS.RESUME
PROCESS.EXIT
```

A redirect is an interaction action. It is not an answer to the active process question and MUST NOT complete the active node.

## 2. Protected state classes

The following state classes are protected by default:

```text
confirmed_contract
confirmed_answers
selected_path
completed_nodes
passed_gates
active_node
active_question
collected_process_data
```

An `unrelated_topic` or `unclassifiable_input` MUST NOT directly mutate protected state.

## 3. Canonical state-protection envelope

```yaml
STATE.PROTECT:
  trigger:
    classification:
      - "unrelated_topic"
      - "unclassifiable_input"

  protected:
    - "confirmed_contract"
    - "confirmed_answers"
    - "selected_path"
    - "completed_nodes"
    - "passed_gates"
    - "active_node"
    - "active_question"
    - "collected_process_data"

  allowed_mutations:
    - "conversation_scope_guard.deviation_counter"
    - "conversation_scope_guard.escalation_level"
    - "execution_trace"

  rollback_on_violation: true
  blocking: true
```

## 4. Response actions

Canonical actions:

```text
gentle_redirect
explicit_scope_reminder
offer_pause_or_exit
suspend_until_process_choice
```

Each action MUST resolve to a response contract.

### `gentle_redirect`

```yaml
required_parts:
  - "brief_acknowledgement"
  - "active_step_reminder"
  - "active_question"
```

### `explicit_scope_reminder`

```yaml
required_parts:
  - "scope_boundary"
  - "state_preserved_notice"
  - "active_question"
```

### `offer_pause_or_exit`

```yaml
required_parts:
  - "repeated_deviation_notice"
  - "active_step_reference"
  - "return_option"
  - "pause_option"
  - "exit_option"
```

### `suspend_until_process_choice`

```yaml
required_parts:
  - "suspension_notice"
  - "state_preserved_notice"
  - "allowed_process_choices"
```

## 5. Response invariants

A scope-guard response MUST NOT:

```text
invent a process answer
confirm a state value
complete the active node
change selected path
mark a gate passed
discard collected state
mark the process completed
silently exit the process
```

The response MAY:

```text
acknowledge the user message
state the process boundary
show the active step
repeat the active question
offer return, pause, or exit
report that state is preserved
```

## 6. Pause semantics

`PROCESS.PAUSE` MUST:

```text
preserve protected state
preserve selected path
preserve active-node resume target
set status = paused
stop normal node execution
emit process.pause.requested and process.paused
```

Pause MUST NOT:

```text
complete the active node
pass pending gates
mark final output ready
reset collected process data
```

## 7. Resume semantics

`PROCESS.RESUME` MUST restore the preserved run context.

Default behavior:

```yaml
PROCESS.RESUME:
  restore:
    - "selected_path"
    - "confirmed_contract"
    - "confirmed_answers"
    - "collected_process_data"
  resume_at: "preserved_active_node"
  recheck:
    - "active_node_preconditions"
    - "blocking_gates"
  reset_deviation_counter: true
```

If the preserved node is no longer valid after a controlled requirement change, the runtime MUST route to the nearest valid re-entry node.

## 8. Exit semantics

`PROCESS.EXIT` is a controlled terminal transition.

Default status:

```text
exited_incomplete
```

Exit MUST NOT produce `completed` unless the process completion contract was already satisfied before the exit request.

Exit record SHOULD preserve:

```text
last active node
selected path
confirmed contract fields
pending gates
reason or user request reference
```

## 9. Correction, backtracking, and requirement change

The guard MUST bypass redirect behavior for:

```text
correction
backtrack_request
requirement_change
```

These intents use controlled state-change flows.

A correction MUST invalidate dependent confirmations and gates when their evidence is no longer valid.

A backtrack MUST route to a declared predecessor or re-entry node.

A requirement change MUST reopen the affected contract and recalculate dependent path/gate validity.

## 10. Safety and error bypass

`unsafe_or_emergency_message` MUST bypass normal scope redirection.

The guard MUST NOT suppress a safety or critical error message because it is outside the process topic.

The bypass itself SHOULD be traced without recording private chain-of-thought.

## 11. State-protection violation behavior

If a response or handler mutates protected state illegally:

```yaml
on_state_protection_violation:
  rollback_mutation: true
  status: "blocked"
  gate_status: "failed"
  diagnostic: "CSG301_PROTECTED_STATE_MUTATION"
  emit_trace: true
```

The runtime MUST NOT continue from the illegally mutated state.

## 12. Diagnostics

```text
CSG301_PROTECTED_STATE_MUTATION
CSG302_REDIRECT_COMPLETED_NODE
CSG303_REDIRECT_CHANGED_PATH
CSG304_REDIRECT_CONFIRMED_STATE
CSG305_REDIRECT_PASSED_GATE
CSG306_REDIRECT_MARKED_COMPLETE
CSG307_PAUSE_LOST_STATE
CSG308_RESUME_TARGET_INVALID
CSG309_EXIT_MARKED_COMPLETE
CSG310_CORRECTION_DEPENDENCIES_NOT_INVALIDATED
CSG311_BACKTRACK_TARGET_INVALID
CSG312_REQUIREMENT_CHANGE_NOT_REOPENED
CSG313_SAFETY_BYPASS_SUPPRESSED
CSG314_RESPONSE_CONTRACT_INCOMPLETE
```

All diagnostics except `CSG308` are blocking by default. `CSG308` requires controlled re-entry resolution.

## 13. Trace events

Required trace events:

```text
conversation.redirect.emitted
conversation.state_protection.activated
conversation.state_protection.violation
conversation.scope_guard.bypassed_for_control_intent
conversation.scope_guard.bypassed_for_safety
process.pause.requested
process.paused
process.resume.requested
process.resumed
process.exit.requested
process.exited
```

Example:

```yaml
event_type: "conversation.state_protection.activated"
node_id: "N_CONFIRM_SOURCE_FIELD"
classification: "unrelated_topic"
protected_state_changed: false
allowed_mutations:
  - "conversation_scope_guard.deviation_counter"
  - "conversation_scope_guard.escalation_level"
action: "explicit_scope_reminder"
```

## 14. Minimum regression set

Required tests:

```text
redirect does not complete node
redirect does not change path
redirect does not confirm state
redirect does not pass gate
redirect does not mark complete
deviation counter may change
trace may change
pause preserves state
resume restores state
resume rechecks preconditions
exit returns exited_incomplete
correction invalidates dependent gates
backtrack uses valid re-entry
requirement change reopens contract
safety bypass is not suppressed
illegal protected-state mutation rolls back
```

## 15. Conformance

CSG-3 conforms when:

- protected state classes are explicit;
- redirect actions resolve to response contracts;
- unrelated and unclassifiable input cannot mutate protected state;
- pause preserves run context;
- resume restores and rechecks run context;
- exit is terminal but not falsely complete;
- correction/backtracking/requirement change use controlled flows;
- safety bypass remains available;
- illegal mutations are rolled back and blocked;
- trace records state-protection behavior.
