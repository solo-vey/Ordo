# Chapter 31. Guided Intake as an Ordo Program

## Why This Is Needed

In many real processes, a model should not create the final result immediately. It first needs to collect data, clarify context, move through a decision tree, check gates, and only then create a document, archive, report, or other artifact.

This mode of work is called `guided intake`.

Simply put, guided intake is a controlled interview with the user in which the model does not improvise the order of questions but follows a defined Ordo program.

This is especially important for complex playbooks, where the wrong first question can break the entire process. For example, the model may ask for an event name too early when it should first determine the path, or it may begin generating the final package before the contract is confirmed.

In an ordinary prompt-based approach, guided intake often looks like this:

```text
Ask me several questions to collect the information.
```

But that is insufficient. The model may:

- ask questions in the wrong order;
- skip a mandatory question;
- confuse a previous answer with a confirmed fact;
- proceed to the result too early;
- fail to record which path was selected;
- fail to explain why some options were rejected and others accepted.

In Ordo, guided intake is not merely a “conversation.” It is a complete Ordo program.

---

## Simple Explanation

Guided intake can be imagined as a form filled in through dialogue rather than on a single page.

The important difference is that this “form” has logic:

```text
if the answer is this → go here;
if data is missing → ask a question;
if a gate has not passed → stop;
if the contract is confirmed → proceed to the next stage;
if the user changes a decision → update state and return to the required node.
```

Guided intake is therefore a combination of:

```text
ENTRY → NODE → STATE → QUESTION → ANSWER → GATE → PATH → NEXT NODE
```

In such a process, the model should not merely “be helpful.” It must act as a controlled process operator.

---

## How Guided Intake Differs from Ordinary Dialogue

Ordinary dialogue may be free-form. The user says something, the model responds, the topic changes, and later the model asks for clarification.

Guided intake has a different nature.

Every question has a purpose:

```text
the question collects a specific state field;
the question is bound to a specific NODE;
the answer must be classified;
after the answer, a state update is performed;
then a gate is checked;
then the next NODE is determined.
```

For example, if an Ordo program creates a new historical event, the question:

```text
What is the event alias?
```

is not merely a conversational question. It is an operation that collects a contract field:

```yaml
node:
  id: "N_COLLECT_ALIAS"
  asks_for: "event.alias"
  required: true
  next_if_answered: "N_COLLECT_SOURCE_FIELD"
```

---

## Basic Guided Intake Elements

Guided intake requires the following Ordo elements:

```text
ENTRY.DEF
NODE.DEF
QUESTION.DEF
ANSWER.REGISTRY
STATE.SCHEMA
STATE.UPDATE
PATH.SELECT
GATE.REPORT
NEXT.NODE
STATUS.SEMANTICS
```

### `ENTRY.DEF`

Defines where the process begins.

```yaml
entry:
  id: "history_event_intake"
  purpose: "guided intake for a new History Event"
  start_node: "N_CLASSIFY_INPUT"
```

### `NODE.DEF`

Describes one dialogue node.

```yaml
node:
  id: "N_CLASSIFY_INPUT"
  type: "decision"
  purpose: "understand what kind of event request this is"
  allowed_next:
    - "N_PATH_A1"
    - "N_PATH_A2"
    - "N_PATH_A4"
    - "N_NEED_MORE_CONTEXT"
```

### `QUESTION.DEF`

Describes which question may be asked.

```yaml
question:
  id: "Q_SOURCE_FIELD"
  node: "N_COLLECT_SOURCE_FIELD"
  text: "Which source field is changing?"
  writes_to: "state.contract.source_field"
  required: true
```

### `ANSWER.REGISTRY`

Records user answers not as “text in chat” but as state values.

```yaml
answer:
  question_id: "Q_SOURCE_FIELD"
  raw_text: "status"
  normalized_value: "item.status"
  confidence: "confirmed"
```

### `STATE.UPDATE`

Shows exactly what changed after an answer.

```yaml
state_update:
  field: "contract.source_field"
  before: null
  after: "item.status"
  source: "user_answer"
```

---

## One Main Question at a Time

An important guided-intake rule is:

```text
one NODE — one main question
```

This does not mean the model can never ask a clarification. But the main movement of the process should remain controlled.

Bad:

```text
What are the alias, source field, old value, new value, display name, path, and QA scenarios?
```

This overloads the user and mixes several state transitions.

Good:

```text
Current step: we need to determine the event alias.
Which alias should we use?
```

After the answer, the model updates state and proceeds to the next node.

---

## Current Status Must Be Visible

Guided intake must always know where it is.

A minimum service status may look like this:

```yaml
intake_status:
  current_entry: "history_event_intake"
  current_node: "N_COLLECT_ALIAS"
  selected_path: "A1"
  confirmed:
    - "event_type"
    - "source_row"
  pending:
    - "alias"
    - "source_field"
    - "old_new_values"
  blocked_by:
    - "G_CONTRACT_COMPLETE"
```

In normal mode, the model does not necessarily show the complete status to the user. But it must be available in debug mode.

---

## Path Selection in Guided Intake

One of the main functions of guided intake is selecting the correct path.

For example:

```text
A1 — field change in the primary source row;
A2 — field change in a related entity;
A4 — external ExternalHistoryEvent;
A5 — no-op or expected-no-change scenario.
```

The model must not simply guess. It must execute `PATH.SELECT`.

```yaml
trace_source: "model_self_report"
path_selection:
  candidate_paths:
    - id: "A1"
      condition: "direct source field change"
    - id: "A2"
      condition: "related entity through identification center"
    - id: "A4"
      condition: "external history event input"

  selected:
    id: "A1"
    reason: "user confirmed direct field change in source row"

  rejected:
    - id: "A2"
      reason: "no related entity context confirmed"
    - id: "A4"
      reason: "input is not ExternalHistoryEvent"
```

This is especially important because an early path-selection error often produces the wrong package at the end.

---

## Gates in Guided Intake

Guided intake should not become an endless interview. It needs control points.

For example:

```text
G_PATH_CONFIRMED
G_CONTRACT_COMPLETE
G_SOURCE_ROW_CONFIRMED
G_VALUES_CONFIRMED
G_QA_SCOPE_CONFIRMED
G_PRE_PACKAGE_APPROVAL
```

A gate does not merely “remind.” It blocks further movement.

```yaml
gate:
  id: "G_CONTRACT_COMPLETE"
  method: mechanical
  trust_class: deterministic
  type: "blocking"
  requires:
    - "contract.alias"
    - "contract.source_field"
    - "contract.values"
    - "contract.source_row"
  on_fail:
    action: "ask_missing_question"
```

If the contract is incomplete, the model is not allowed to proceed to final output generation.

---

## How Guided Intake Handles User Clarifications

The user may change a decision.

For example:

```text
go back to the previous step
I change my decision to 3
```

Ordo should not ignore this. It should perform a controlled state correction.

```yaml
state_correction:
  reason: "user changed previous decision"
  affected_field: "selected_option"
  before: "2"
  after: "3"
  rollback_to_node: "N_CONFIRM_OPTION"
  recheck_gates:
    - "G_PATH_CONFIRMED"
    - "G_CONTRACT_COMPLETE"
```

This is very important. In complex processes, users often clarify or change previous decisions. If guided intake does not support controlled rollback, state quickly becomes unreliable.

---

## Guided Intake and Debug Mode

In debug mode, guided intake should show:

```text
- the current NODE;
- why this specific question was asked;
- which state field it fills;
- which paths remain unresolved;
- which gates block progress;
- which answers are already confirmed;
- which decisions were changed by the user;
- why the model is not proceeding to final output.
```

Example debug fragment:

```yaml
debug:
  current_node: "N_COLLECT_SOURCE_FIELD"
  question_reason: "contract.source_field is required for Path A1"
  writes_to: "state.contract.source_field"
  blocked_gates:
    - "G_CONTRACT_COMPLETE"
  next_after_answer:
    - "N_COLLECT_VALUES"
```

---

## Guided Intake and the Improvement Loop

Guided intake is one of the main places where improvements emerge.

The user may say:

```text
this question should have been asked earlier
```

or:

```text
you should not ask for the alias here; determine the source row first
```

Ordo should create an improvement record:

```yaml
improvement_record:
  type: "intake_order_problem"
  affected_unit:
    kind: "node"
    id: "N_COLLECT_ALIAS"
  proposed_patch:
    - "move N_COLLECT_SOURCE_ROW before N_COLLECT_ALIAS"
  suggested_test:
    id: "TC_SOURCE_ROW_BEFORE_ALIAS"
```

This allows guided intake to improve through a controlled improvement cycle rather than chaotic instruction rewriting.

---

## Guided Intake as Compiled IR

In compiled IR, guided intake may look like a set of opcodes:

```json
[
  {
    "op": "ENTRY.DEF",
    "id": "history_event_intake",
    "start_node": "N_CLASSIFY_INPUT"
  },
  {
    "op": "NODE.DEF",
    "id": "N_COLLECT_ALIAS",
    "node_type": "question",
    "writes_to": "contract.alias"
  },
  {
    "op": "QUESTION.DEF",
    "id": "Q_ALIAS",
    "text": "What is the event alias?",
    "required": true
  },
  {
    "op": "GATE.DEF",
    "id": "G_CONTRACT_COMPLETE",
    "type": "blocking"
  },
  {
    "op": "STATE.UPDATE",
    "from": "Q_ALIAS",
    "to": "contract.alias"
  }
]
```

This means guided intake can be not only described in words but executed as a structured program.

---

## Typical Mistakes

### Mistake 1. Turning Guided Intake into an Ordinary Question List

A list of questions is not guided intake if there is no state, gates, or path logic.

### Mistake 2. Asking Everything at Once

When the model asks ten things simultaneously, it loses control of state.

### Mistake 3. Failing to Record What Was Confirmed

If the model does not distinguish “the user mentioned” from “the user confirmed,” it may create an incorrect contract.

### Mistake 4. Not Supporting Rollback

Users often change decisions. Ordo must be able to update state correctly.

### Mistake 5. Allowing Final Output Before Gates

Guided intake must block premature artifact generation.

---

## Mini-Exercise

Take a simple process:

```text
Prepare a response to a customer complaint.
```

Try to determine:

```text
1. Which ENTRY starts the process?
2. Which 3–5 NODEs are needed?
3. What first question should the model ask?
4. Which state fields must be collected?
5. Which gate should exist before the final text?
6. What should happen if the user changes the tone from “formal” to “friendly”?
```

---

## Short Summary

Guided intake is not merely a dialogue with a model. It is an Ordo program that controls information collection, path selection, state updates, gates, and transitions between nodes.

Its main value is that a complex process does not turn into chaotic correspondence. The model knows where it is, what has already been confirmed, what still needs to be collected, and why it is not allowed to move forward.

In large playbooks, guided intake is the bridge between human conversation and formal Ordo execution.
