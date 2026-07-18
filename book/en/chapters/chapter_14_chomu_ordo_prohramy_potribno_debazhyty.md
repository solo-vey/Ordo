# Chapter 14. Why Ordo Programs Need Debugging

## Why This Is Needed

When a normal program behaves incorrectly, a developer does not inspect only the final screen. They look at logs, variable values, branches, errors, and the sequence of executed operations.

AI processes need the same discipline.

A model may produce a plausible final answer while internally following the wrong path, skipping a gate, changing state incorrectly, or using knowledge that was never authorized by the process.

Without debug information, the author sees only:

```text
input
↓
model
↓
final answer
```

If the result is wrong, the only practical reaction is often:

```text
rewrite the prompt and try again
```

Ordo treats this as insufficient.

An Ordo program should make important execution events observable.

![Nebu — idea: debug makes process behavior observable](../assets/mascots/64x64/Nebu_idea_64x64.png)

## Simple Explanation

Debugging means answering:

```text
What exactly happened during this run?
```

For an Ordo process, this includes questions such as:

```text
Which execution mode was active?
Which entry point was used?
Which path was selected?
Which paths were rejected?
Which decision caused the selection?
What state existed before the step?
What changed after the step?
Which gate ran?
How was the gate checked?
What evidence supported its result?
Which knowledge source was used?
Which warning or violation appeared?
```

The final text alone cannot answer these questions.

That is why Ordo includes a debug and trace layer.

## Why This Is Especially Important for AI

A traditional program executes explicit instructions. If the code says:

```text
if severity == critical:
    path = emergency
```

we can inspect the code and runtime values.

A language model works differently. It interprets context and produces a result probabilistically. Even when the process is structured, the model may:

- overgeneralize;
- interpret a short answer too broadly;
- use a nearby but incorrect rule;
- silently skip a negative condition;
- infer a state transition that was not authorized;
- treat an example as a rule;
- continue after a blocking condition.

This creates a dangerous situation:

```text
the final answer looks reasonable
but the execution logic was wrong
```

Debugging is needed to reveal such errors before they become hidden process behavior.

## Ordo Construct

Ordo defines execution modes such as:

```text
normal
debug
dry_run
test
replay
improvement_capture
```

A program may activate debug mode:

```yaml
execution:
  mode: "debug"
```

Or in IR:

```json
{
  "op": "DEBUG.MODE",
  "mode": "debug"
}
```

In debug mode, the process may emit structured diagnostic artifacts:

```text
TRACE.LOG
DECISION.LOG
PATH.EXPLAIN
STATE.SNAPSHOT
STATE.DIFF
GATE.REPORT
KNOWLEDGE.TRACE
```

These are not decorative notes. They form an observable execution layer.

## Small Example Without Debug

Imagine a guided intake process.

The user answers:

```text
We need to add a new event type.
```

The model chooses Path 2 and starts asking questions.

Later, the author discovers that Path 1 should have been selected.

Without debug information, the available evidence may be only:

```text
User message
Model questions
```

The author must guess:

```text
Did the model misunderstand the request?
Did it read the wrong path rule?
Did it interpret a synonym incorrectly?
Did state already contain a value from an earlier step?
Did it skip a gate?
```

The process is difficult to diagnose.

## Small Example with Debug

With debug mode, the process may record:

```yaml
trace_source: "model_self_report"
run_id: "RUN-2026-0142"

path_explain:
  selected_path: "PATH_2"
  candidates:
    - path: "PATH_1"
      status: "rejected"
      reason: "request interpreted as modification of existing event"
    - path: "PATH_2"
      status: "selected"
      reason: "phrase 'add a new event type' mapped to extension flow"

decision_log:
  - decision_id: "D_PATH_SELECTION"
    input_ref: "USER_MESSAGE_1"
    result: "PATH_2"

state_diff:
  before:
    selected_path: null
  after:
    selected_path: "PATH_2"
```

Now the problem is visible.

The author can inspect the path-selection rule rather than rewriting the whole playbook.

## Debug as Protection Against Overconfident Answers

![Nebu — attention: a confident answer may hide an incorrect path](../assets/mascots/64x64/Nebu_attention_64x64.png)

AI models often produce fluent text even when the process behind it is wrong.

Therefore:

```text
good wording != correct execution
```

Debug mode separates these two dimensions.

A result may look polished but have:

```text
wrong path
skipped gate
unsupported state update
wrong knowledge source
unrecorded assumption
```

A debug trace makes these defects visible.

This is especially important for playbooks that create technical packages, contracts, Jira tasks, QA artifacts, migration instructions, or other outputs where process correctness matters more than stylistic quality.

## Debug and State

State is one of the first places to inspect when a process behaves unexpectedly.

Suppose the model asks the same question twice.

The problem may not be the question text. The real problem may be that the answer was never written to state.

A state snapshot may show:

```yaml
state:
  alias_confirmed: false
  source_row_confirmed: true
```

A state diff may show:

```yaml
before:
  alias_confirmed: false

after:
  alias_confirmed: false
```

although the user explicitly confirmed the alias.

This immediately localizes the defect:

```text
the node received the answer
but STATE.UPDATE did not occur
```

Without state debugging, the author may incorrectly rewrite the conversational prompt.

## Debug and Path Selection

A path-selection error should be explainable.

A good debug record does not contain only:

```text
selected PATH_3
```

It should also show rejected candidates:

```yaml
path_explain:
  selected: "PATH_3"
  candidates:
    - id: "PATH_1"
      result: "rejected"
      reason: "no new entity requested"
    - id: "PATH_2"
      result: "rejected"
      reason: "no migration requested"
    - id: "PATH_3"
      result: "selected"
      reason: "existing behavior requires extension"
```

Rejected paths matter because the bug may be in a rejection condition rather than in the selected path itself.

## Debug and Knowledge

A model may produce the wrong answer because it used the wrong knowledge source.

Ordo therefore needs knowledge trace.

For example:

```yaml
knowledge_trace:
  - source_id: "domain_pack.history_event"
    version: "0.12.0"
    used_by: "NODE_SOURCE_ROW"
    purpose: "field semantics"

  - source_id: "freeform.note.17"
    used_by: "NODE_SOURCE_ROW"
    purpose: "example interpretation"
```

This allows the reviewer to ask:

```text
Was the correct domain pack loaded?
Was an obsolete library version used?
Did a FREEFORM example accidentally influence a hard rule?
Was required documentation never loaded?
```

Knowledge use should be observable when it affects important decisions.

## Typical Mistakes

### Mistake 1. Debugging Only the Final Text

The final text is an output artifact, not a complete execution record.

If the wrong path produced a good-looking document, editing the document template does not fix the process.

### Mistake 2. Not Logging Rejected Paths

Recording only the selected path hides why alternatives were discarded.

A path bug often lives in a rejection rule.

### Mistake 3. Not Logging State Changes

A current state snapshot is useful, but it does not show how the state changed.

`STATE.DIFF` is needed to answer:

```text
what changed at this exact step?
```

### Mistake 4. Treating Debug as Unnecessary for Playbooks

A playbook is executable process logic expressed for a model.

The more nodes, gates, statuses, outputs, and approvals it contains, the more important debugging becomes.

### Mistake 5. Confusing Debug Trace with Chain of Thought

![Nebu — thinking: execution trace is structured evidence, not hidden reasoning](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Ordo does not require private chain-of-thought disclosure.

A debug trace should contain observable process facts:

```text
operation executed
path selected
state changed
gate checked
evidence reference used
status produced
warning recorded
```

It should not require unrestricted hidden reasoning.

This distinction is essential.

### Mistake 6. Not Preserving `run_id`

Without a stable run identifier, logs from several executions may be mixed.

Every diagnostic run should be attributable to one execution:

```yaml
run_id: "RUN-2026-0142"
```

The same identifier should connect trace, gate reports, state diffs, validation artifacts, and replay records.

## Mini-Exercise

Take a process that has at least three steps.

For example:

```text
collect request
select path
generate document
```

Imagine that the final document is wrong.

Write five debug questions:

```text
1. Which path was selected?
2. Which paths were rejected?
3. What state existed before generation?
4. Which gate passed before generation?
5. Which knowledge source was used?
```

Then define which Ordo diagnostic artifact should answer each question:

```text
PATH.EXPLAIN
STATE.SNAPSHOT
STATE.DIFF
GATE.REPORT
KNOWLEDGE.TRACE
```

If the process cannot answer these questions, it is difficult to debug.

## Short Summary

Ordo programs need debugging because a plausible final answer does not prove correct execution.

The author must be able to inspect:

```text
execution mode
run ID
selected and rejected paths
decisions
state snapshots
state changes
gate results
knowledge sources
warnings and violations
```

Ordo therefore treats debug and trace as part of the language and IR rather than as optional comments around the prompt.

The main principle is:

```text
If a process can make an important decision,
the process should be able to leave structured evidence of that decision.
```

Debugging does not ask the model to expose hidden chain of thought. It asks the Ordo program to record observable execution facts.
