# Ordo Optional Capability Contract: Conversation Scope Guard

**Contract ID:** `ORDO-CAP-CSG-001`  
**Capability name:** `Conversation Scope Guard`  
**Status:** production-ready optional capability; disabled by default in Ordo Core  
**Language line:** `CSG`  
**Applicability:** optional  
**Default in Ordo Core:** disabled  
**Primary use:** guided intake, decision-tree processes, controlled interviews, regulated or high-discipline workflows

**Maturity:**

```yaml
specification: language_integrated
schema_support: integrated
toolchain_support: integrated
runtime_enforcement: integrated_helper_runner
model_benchmark: passed_cross_model_repeated_runs
production_recommendation: ready
```

---

## 1. Purpose

`Conversation Scope Guard` is an optional Ordo capability that controls how an active process reacts when a user message does not directly answer the current process question or appears to move outside the active process scope.

The capability exists to:

- preserve the active process state;
- prevent unrelated messages from completing a node;
- prevent accidental path or confirmed-state changes;
- distinguish legitimate process-control messages from unrelated topics;
- redirect the conversation according to an explicitly selected strictness mode;
- escalate repeated deviations without losing the process context;
- record deviation handling in `EXECUTION_TRACE`.

This capability is not mandatory for every Ordo program.

---

## 2. Architectural Position

`Conversation Scope Guard` is not a separate runtime and does not replace existing Ordo constructs.

It is an optional interaction-control capability that compiles into and uses:

```text
NODE.DEF
QUESTION.DEF
ANSWER.REGISTRY
STATE.SCHEMA
STATE.UPDATE
STATUS.SEMANTICS
ASSERTION
GATE.CHECK
PROCESS.PAUSE
PROCESS.RESUME
PROCESS.EXIT
EXECUTION_TRACE
```

The capability may be activated by:

- a playbook;
- a Guided Intake Profile;
- another conversation-control Profile;
- a Domain Pack;
- a process-specific contract.

It must not be enabled implicitly.

---

## 3. Capability Declaration

Minimum declaration:

```yaml
conversation_scope_guard:
  supported: true
  enabled: true
  mode: guided_redirect
```

Disabled declaration:

```yaml
conversation_scope_guard:
  supported: true
  enabled: false
```

A program that does not declare this capability must behave as though:

```yaml
conversation_scope_guard:
  supported: false
  enabled: false
```

---

## 4. Canonical Source Construct

```yaml
CONVERSATION.SCOPE.DEF:
  id: "CSG_MAIN"
  enabled: true
  mode: "guided_redirect"

  scope:
    process_id: "PROCESS_ID"
    active_node_ref: "STATE.current_node"
    active_question_ref: "STATE.current_question"
    accepted_context:
      - "answer_to_active_question"
      - "clarification"
      - "correction"
      - "backtrack_request"
      - "requirement_change"
      - "pause_request"
      - "resume_request"
      - "exit_request"
      - "process_meta_question"
      - "related_context"
      - "safety_or_error_message"

  out_of_scope_behavior:
    answer_external_question: false
    acknowledge_message: true
    repeat_active_question: true
    preserve_state: true
    complete_active_node: false
    change_selected_path: false
    confirm_state_value: false

  escalation:
    counter_scope: "active_node"
    reset_on:
      - "valid_process_answer"
      - "node_transition"
      - "process_resume"

    levels:
      1: "gentle_redirect"
      2: "explicit_scope_reminder"
      3: "offer_pause_or_exit"
      4: "suspend_until_process_choice"

  trace:
    required: true
```

---

## 5. Deviation Classification Contract

A message that does not directly answer the active question must not automatically be classified as out of scope.

The implementation must first classify it into one of the following canonical types:

```yaml
deviation_types:
  - answer_to_active_question
  - clarification
  - correction
  - backtrack_request
  - requirement_change
  - pause_request
  - resume_request
  - exit_request
  - process_meta_question
  - related_context
  - unrelated_topic
  - unsafe_or_emergency_message
  - unclassifiable_input
```

### 5.1. Semantic Requirements

- `clarification` asks for explanation of the active step or active question.
- `correction` changes or corrects a previously supplied answer.
- `backtrack_request` asks to return to an earlier node or decision.
- `requirement_change` changes the process contract or intended output.
- `pause_request` temporarily suspends the run without losing state.
- `resume_request` continues a previously paused run.
- `exit_request` ends the run through a controlled terminal transition.
- `process_meta_question` asks about the current process, status, rules, or next action.
- `related_context` provides information relevant to the current or downstream process.
- `unrelated_topic` is outside the declared process scope.
- `unsafe_or_emergency_message` has priority over normal scope handling.
- `unclassifiable_input` requires clarification and must not be treated as a valid answer.

---

## 6. Strictness Modes

The capability defines four canonical modes.

### 6.1. `advisory`

The model may provide a short answer to the unrelated topic and then return to the active process.

```yaml
advisory:
  answer_external_question: true
  max_external_answer_scope: "brief"
  redirect_after_answer: true
```

### 6.2. `guided_redirect`

The model does not develop the unrelated topic. It acknowledges the message, explains the active boundary, and returns to the current step.

```yaml
guided_redirect:
  answer_external_question: false
  acknowledge_message: true
  explain_scope_boundary: true
  repeat_active_question: true
```

### 6.3. `strict_redirect`

The model states that the message is outside the active process scope and repeats the active process question.

```yaml
strict_redirect:
  answer_external_question: false
  acknowledge_message: false
  scope_notice: true
  repeat_active_question: true
```

### 6.4. `locked_process`

Only explicitly allowed process-control and process-answer intents are accepted.

```yaml
locked_process:
  allowed_intents:
    - "answer_to_active_question"
    - "clarification"
    - "correction"
    - "backtrack_request"
    - "requirement_change"
    - "pause_request"
    - "resume_request"
    - "exit_request"
    - "process_meta_question"
    - "unsafe_or_emergency_message"
```

---

## 7. State-Protection Invariants

The following assertions are normative when the capability is enabled.

```yaml
assertions:
  - id: "A_DEVIATION_DOES_NOT_COMPLETE_NODE"
    polarity: "not"
    condition: "out_of_scope_message_completed_active_node"
    severity: "block"

  - id: "A_DEVIATION_DOES_NOT_CHANGE_PATH"
    polarity: "not"
    condition: "out_of_scope_message_changed_selected_path"
    severity: "block"

  - id: "A_DEVIATION_DOES_NOT_CONFIRM_STATE"
    polarity: "not"
    condition: "out_of_scope_message_confirmed_state_value"
    severity: "block"

  - id: "A_DEVIATION_DOES_NOT_RESET_STATE"
    polarity: "not"
    condition: "out_of_scope_message_reset_collected_state"
    severity: "block"

  - id: "A_UNCLASSIFIABLE_INPUT_IS_NOT_ACCEPTED_AS_ANSWER"
    polarity: "not"
    condition: "unclassifiable_input_completed_active_question"
    severity: "block"

  - id: "A_SCOPE_GUARD_DOES_NOT_BLOCK_CONTROL_INTENT"
    polarity: "not"
    condition: "valid_process_control_intent_blocked_as_unrelated"
    severity: "block"

  - id: "A_SCOPE_GUARD_DOES_NOT_BLOCK_SAFETY"
    polarity: "not"
    condition: "unsafe_or_emergency_message_suppressed_by_scope_guard"
    severity: "block"
```

---

## 8. Escalation Contract

Repeated unrelated messages may escalate, but escalation must be scoped and reset predictably.

```yaml
DEVIATION.ESCALATE:
  counter_scope: "active_node"

  reset_on:
    - "valid_process_answer"
    - "node_transition"
    - "process_resume"

  levels:
    1:
      action: "gentle_redirect"

    2:
      action: "explicit_scope_reminder"

    3:
      action: "offer_pause_or_exit"

    4:
      action: "suspend_until_process_choice"
```

A deviation counter must not be global across the entire process unless explicitly declared.

A node transition resets the default counter.

---

## 9. Response Contract

A redirect response may contain:

```text
acknowledgement
scope notice
current process status
active node
active question
allowed next actions
pause / exit options
```

It must not:

```text
silently mark the current step complete
invent an answer for the user
change confirmed state
change path
discard collected state
terminate the run without an exit request or terminal rule
```

Recommended response templates:

```yaml
response_templates:
  gentle_redirect:
    required_parts:
      - "brief_acknowledgement"
      - "active_step_reminder"
      - "active_question"

  explicit_scope_reminder:
    required_parts:
      - "scope_boundary"
      - "state_preserved_notice"
      - "active_question"

  offer_pause_or_exit:
    required_parts:
      - "repeated_deviation_notice"
      - "return_option"
      - "pause_option"
      - "exit_option"

  suspend_until_process_choice:
    required_parts:
      - "suspension_notice"
      - "allowed_process_choices"
```

---

## 10. Process-Control Operations

The capability may use the following canonical operations:

```text
DEVIATION.CLASSIFY
DEVIATION.HANDLE
DEVIATION.ESCALATE
STATE.PROTECT
PROCESS.PAUSE
PROCESS.RESUME
PROCESS.EXIT
```

### 10.1. `PROCESS.PAUSE`

Must preserve current process state and active node unless the process contract explicitly says otherwise.

### 10.2. `PROCESS.RESUME`

Must restore the preserved process state and return to the suspended node or a declared resume node.

### 10.3. `PROCESS.EXIT`

Must use a controlled terminal status and must not falsely mark the process result as complete.

---

## 11. Status Semantics

Recommended statuses:

```yaml
status_semantics:
  active:
    meaning: "process is running and accepts valid process input"

  deviation_detected:
    meaning: "message requires classification before state mutation"

  redirect_required:
    meaning: "message is outside scope and requires redirect behavior"

  awaiting_process_choice:
    meaning: "process is suspended until return, pause, or exit is selected"

  paused:
    meaning: "process state is preserved but normal execution is suspended"

  exited_incomplete:
    meaning: "run ended before the process contract was completed"
```

---

## 12. EXECUTION_TRACE Events

When trace is enabled, the capability must support the following events:

```text
conversation.deviation.detected
conversation.deviation.classified
conversation.redirect.emitted
conversation.escalation.changed
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
event_type: "conversation.deviation.classified"
node_id: "N_CONFIRM_SOURCE_FIELD"
classification: "unrelated_topic"
mode: "guided_redirect"
escalation_level: 2
state_changed: false
action: "explicit_scope_reminder"
```

---

## 13. Compilation Requirements

The compiler must:

1. validate the declared mode;
2. validate the deviation taxonomy;
3. expand state-protection invariants into assertions;
4. bind escalation counters to their declared scope;
5. generate trace hooks when `trace.required: true`;
6. reject undefined response actions;
7. preserve pause, resume, exit, correction, backtracking, requirement change, and safety exceptions;
8. emit a diagnostic if the guard can mutate confirmed state for an unrelated message;
9. emit a diagnostic if `locked_process` has no escape actions;
10. emit a diagnostic if escalation has no terminal or controlled suspension behavior.

---

## 14. Validation Requirements

A program using this capability should include tests for:

```text
valid answer to active question
clarification
correction
backtracking
requirement change
pause
resume
exit
process meta-question
related context
first unrelated message
repeated unrelated messages
unclassifiable input
safety or emergency message
state preservation
path preservation
confirmed-state preservation
counter reset after valid answer
counter reset after node transition
```

Minimum regression assertions:

```text
out-of-scope input does not complete node
out-of-scope input does not change path
out-of-scope input does not confirm state
out-of-scope input does not reset state
valid control intents are not blocked
safety messages are not blocked
pause preserves state
resume restores state
exit produces incomplete terminal status
```

---

## 15. Applicability Guidance

Recommended uses:

```text
guided intake
decision-tree interviews
regulated workflows
high-discipline package generation
long-running process conversations
processes with expensive or dangerous state transitions
```

Usually unnecessary for:

```text
single-turn transformations
simple writing requests
open brainstorming
casual conversation
processes without persistent state or controlled paths
```

---

## 16. APF Integration Rule

APF must not enable this capability for itself by default.

```yaml
conversation_scope_guard:
  enabled: false
```

APF may include a separate design phase for playbooks it creates:

```text
process rail confirmed
→ conversation deviation policy design
→ user confirmation
→ guard source generation
→ guard tests
→ package assembly
```

The phase should determine:

```text
whether the guard is needed
strictness mode
accepted context
deviation taxonomy
escalation policy
state-protection rules
response templates
pause/resume/exit behavior
trace events
regression tests
```

Recommended generated-playbook default for guided processes:

```yaml
conversation_scope_guard:
  supported: true
  enabled: true
  mode: "guided_redirect"
  state_change_on_out_of_scope: false
```

This is an APF recommendation, not a universal language default.

---

## 17. Conformance

A program conforms to this contract when:

- the capability is declared explicitly;
- mode semantics are explicit;
- legitimate control intents are distinguished from unrelated topics;
- state-protection invariants are active;
- escalation is scoped and reset predictably;
- pause/resume/exit behavior is defined;
- trace events are available when required;
- regression tests protect the invariants;
- an unrelated message cannot complete the active process step.

---

## 18. Non-Goals

This capability does not:

- decide the business scope of a process automatically;
- replace process design;
- replace `ANSWER.REGISTRY`;
- prohibit users from changing requirements;
- prohibit pause, resume, exit, correction, clarification, or backtracking;
- expose private chain of thought;
- force every Ordo program into a locked conversation mode.
