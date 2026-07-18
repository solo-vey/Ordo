# Chapter 15. Debug Mode and Diagnostic Trace

## Why This Is Needed

In the previous chapter, we established the main problem: a complex Ordo program cannot be developed properly if only the model's final answer is visible.

The final answer is only the top of the process. It shows what the model said at the end, but not how it arrived there.

For simple tasks, this is sometimes enough. If a model rewrites a short message, for example, the result can simply be judged: does it sound good or not?

But this is insufficient for a playbook, domain pack, library, or multi-step process. There it is important to know:

```text
- which path was selected;
- which paths were rejected;
- which rules triggered;
- which gates were checked;
- which gates were skipped;
- what the state was before the step;
- what the state became after the step;
- which knowledge or instruction fragments were used;
- where the model made an assumption;
- where it should have stopped but did not.
```

This is why Ordo needs `debug mode`.

`Debug mode` is an execution mode in which an Ordo program not only produces a result but also forms a complete execution trace.

![Nebu — idea: debug mode shows the execution path](../assets/mascots/64x64/Nebu_idea_64x64.png)

In simple terms:

```text
normal mode answers: what was done;
debug mode answers: why it was done this way.
```

## Simple Explanation

Imagine that an Ordo program is a route in a navigation system.

In normal mode, the navigator simply guides you to the destination.

In debug mode, it additionally shows:

```text
- why it selected this road;
- which roads it rejected;
- where restrictions existed;
- where traffic jams occurred;
- where it rebuilt the route;
- which data it relied on;
- what would have happened if another path had been selected.
```

For Ordo, this means the model must show not hidden reasoning but a formal execution trace.

This distinction is important.

Ordo must not require a model to disclose private chain of thought. Instead, Ordo must require a structured execution trace: a record of formal decisions that are part of the process.

![Nebu — attention: trace is not chain of thought](../assets/mascots/64x64/Nebu_attention_64x64.png)

We do not need to see everything the model “thought.” We need to see what it **executed**:

```text
- which NODE is active;
- which path was selected;
- which gate was evaluated;
- which state changed;
- which output was allowed;
- which rule was used;
- which warning was raised.
```

This is not model psychology. It is a program execution log.

## Debug Mode as Part of the Language

In Ordo, debug mode must not be an external comment such as:

```text
Explain why you did this.
```

That is too weak. The model may explain beautifully but not necessarily accurately.

The language needs a formal construct:

```yaml
run:
  mode: debug
  execution_mode: chat_internal
  trace_required: true
```

Or in compiled IR:

```json
{
  "op": "DEBUG.MODE",
  "mode": "debug",
  "execution_mode": "chat_internal",
  "trace_required": true
}
```

This means the Ordo program is launched not only to produce a result but also to collect an execution trace.

In debug mode, a result without a trace is considered incomplete.

In Ordo v0.12, `execution_mode` must be recorded alongside `mode`. It honestly shows the environment in which the process executes:

```text
full_runtime   — transitions and hard gates are forcibly controlled by a runtime or helper runner;
chat_internal  — the model runs the process in chat, but some checks may be performed by code or session files;
freeform_only  — the model follows Ordo discipline through text without external enforcement.
```

This is not a minor technical detail. The same debug trace has different evidentiary strength depending on who actually controlled transitions: code, the model in chat, or textual self-discipline alone.

## What Is an Execution Trace

An `execution trace` is a structured log of Ordo program execution.

It should answer:

```text
what was provided as input;
what the initial state was;
which path was selected;
why that path was selected;
which paths were rejected;
which nodes were traversed;
which gates were checked;
which decisions were made;
which state changes occurred;
which outputs were allowed;
which outputs were blocked;
which sources or knowledge were used;
which warnings or violations occurred.
```

A minimum trace structure may look like this:

```yaml
trace:
  run_id: "RUN-001"
  mode: "debug"
  execution_mode: "chat_internal"
  trace_source: "model_self_report"

  input_snapshot:
    user_message: "create a company status change event"

  selected_path:
    id: "A1"
    reason: "the user described a field change in the main source row"

  rejected_paths:
    - id: "A2"
      reason: "there is no confirmation that the change concerns a related entity"
    - id: "A4"
      reason: "there is no ExternalHistoryEvent"

  nodes:
    - id: "NODE_SELECT_PATH"
      status: "completed"
    - id: "NODE_COLLECT_CONTRACT"
      status: "active"

  gates:
    - id: "G_CONTRACT_CONFIRMED"
      status: "pending"
      reason: "source field has not yet been confirmed"

  state_changes:
    - field: "event_alias"
      before: null
      after: "LU_CHANGE_STATUS"

  warnings:
    - "source field not confirmed"

  violations: []
```

This trace is not the final user document. It is an internal but controlled execution artifact.

## Trace Source

In Ordo v0.12, every trace must explicitly show the source of its trust.

The following field is used:

```yaml
trace_source: model_self_report | runtime_enforced | hybrid
```

`model_self_report` means the trace was formed by the model itself. It is useful for explaining logic but is not the same kind of evidence as an external runtime log.

`runtime_enforced` means the trace was generated by runner or orchestrator code from actual state transitions, actual gate calls, and recorded state snapshots.

`hybrid` means a mixed mode: part of the trace is produced by code and part is the model's semantic explanation. For example, `STATE.DIFF` may be runtime-enforced while `PATH.EXPLAIN.reason` is model self-report.

This field is required for honesty. Without it, a debug trace may look like a classic program log even though it may actually be only the model's structured self-report.

Example:

```yaml
trace:
  run_id: "RUN-001"
  mode: "debug"
  execution_mode: "chat_internal"
  trace_source: "hybrid"

  runtime_enforced:
    - "state_snapshot"
    - "mechanical_gate_status"

  model_self_report:
    - "path_reason"
    - "semantic_evidence_summary"
```

Ordo v0.12 rule: a trace without `trace_source` is incomplete.

## Run ID

Every Ordo program run must have a `run_id`.

Without a `run_id`, it is difficult to understand which exact execution is being discussed.

This is especially important when a user says:

```text
this is where it went wrong
```

Ordo should be able to bind the observation to a concrete run:

```yaml
run:
  id: "RUN-2026-07-05-014"
  program: "history_event_playbook"
  version: "0.12"
  mode: "debug"
  execution_mode: "chat_internal"
  trace_source: "hybrid"
```

An improvement record can then say:

```yaml
observed_in:
  run_id: "RUN-2026-07-05-014"
  node: "NODE_PRE_ARCHIVE_CHECK"
  gate: "G_PACKAGE_SELF_CHECK"
```

This makes the improvement concrete rather than abstract and ties it to an actual execution.

## Input Snapshot

A debug trace should contain an input snapshot.

This does not necessarily mean a full copy of all data, especially when confidential information is present. But it must contain enough to understand how the run began.

For example:

```yaml
input_snapshot:
  user_intent: "create HistoryEvent for a status change"
  provided_fields:
    - "alias"
    - "old_value"
    - "new_value"
  missing_fields:
    - "source_field"
    - "fixture_id"
```

This shows that the model had no right to move to the final package because part of the contract had not yet been confirmed.

## Path Explain

![Nebu — thinking: path explain shows more than the selection](../assets/mascots/64x64/Nebu_thinking_64x64.png)

One of the most important debug-mode elements is `PATH.EXPLAIN`.

It must show not only the selected path but also the reason for the selection.

Bad:

```yaml
selected_path: "A1"
```

Better:

```yaml
selected_path:
  id: "A1"
  reason: "input describes a direct change in the main source row"
  evidence:
    - "user provided old/new values"
    - "no related entity context was confirmed"
```

An even better variant shows rejected paths:

```yaml
rejected_paths:
  - id: "A2"
    reason: "related entity was not confirmed"
  - id: "A4"
    reason: "external history event payload was not provided"
```

This is extremely important for debugging.

Without rejected paths, we see only the decision. With rejected paths, we see the boundaries of the decision.

## Decision Log

`DECISION.LOG` is a log of formal decisions.

A decision is not any sentence produced by the model. It is a point at which the Ordo program could have followed different paths.

For example:

```yaml
decision_log:
  - id: "D001"
    node: "NODE_SELECT_PATH"
    decision: "select_path_A1"
    reason: "direct source row change"
    evidence:
      - "field change described"
      - "no external event"

  - id: "D002"
    node: "NODE_OUTPUT_ALLOWED"
    decision: "block_final_archive"
    reason: "pre-archive approval gate is not passed"
    evidence:
      - "G_PRE_ARCHIVE_APPROVAL = pending"
```

A decision log should be short but sufficiently precise.

It should not become a long literary explanation.

## State Snapshot and State Diff

In a complex Ordo program, state is the memory of the process.

Debug mode must show not only the current state but also state changes.

Two constructs are needed:

```text
STATE.SNAPSHOT
STATE.DIFF
```

`STATE.SNAPSHOT` shows the state at a specific moment.

`STATE.DIFF` shows exactly what changed.

For example:

```yaml
state_snapshot:
  at: "before_NODE_COLLECT_CONTRACT"
  state:
    event_alias: null
    source_field: null
    output_allowed: false
```

After the step:

```yaml
state_diff:
  step: "NODE_COLLECT_ALIAS"
  changes:
    - field: "event_alias"
      before: null
      after: "LU_CHANGE_STATUS"
```

This makes it possible to see where the model filled state prematurely or, conversely, failed to fill something that had already been confirmed.

## Gate Report

In normal mode, a gate may simply block or allow an action.

In debug mode, a gate must explain its status.

For example:

```yaml
gate_report:
  - gate_id: "domain_pack.history_event.G_PRE_ARCHIVE_APPROVAL"
    method: "human"
    trust_class: "human_decision"
    trace_source: "runtime_enforced"
    status: "blocked"
    reason: "user has not approved package generation"
    required_evidence:
      - "explicit user approval"
    actual_evidence: []
```

This is better than simply:

```text
the archive cannot be created
```

because it shows exactly what is missing.

A gate report should contain at least:

```text
- full namespaced gate id;
- method;
- trust_class;
- trace_source;
- status;
- reason;
- required evidence;
- actual evidence;
- blocking / non-blocking;
- next required action.
```

This is especially important for gates with different trust levels. `method: mechanical` and `method: self_verification` may both have `status: passed`, but they do not provide the same type of guarantee. The first passed a deterministic check; the second is a semantic model judgment under an evidence protocol.

## Knowledge Trace

An Ordo program often relies on different sources:

```text
- Core;
- Profile;
- Domain Pack;
- Library;
- user-provided data;
- uploaded playbook;
- runtime context;
- FREEFORM block.
```

In debug mode, it must be visible which knowledge was used.

For example:

```yaml
trace_source: "model_self_report"
knowledge_trace:
  - source_type: "domain_pack"
    source_id: "history_event_domain_pack"
    section: "Path A1"
    used_for: "path selection"

  - source_type: "library"
    source_id: "ordo.validation.contract_first"
    export: "G_CONTRACT_CONFIRMED"
    used_for: "contract validation"

  - source_type: "freeform"
    source_id: "FF_ANALYST_STYLE_GUIDE"
    used_for: "response tone"
```

This is especially important for FREEFORM.

If the model made an important decision based on FREEFORM, the trace must show it. This may reveal that the FREEFORM content should be formalized.

## Warning and Violation

A debug trace must distinguish warnings from violations.

A `warning` is a risk or incompleteness that does not necessarily stop the process.

A `violation` is a rule breach.

For example:

```yaml
warnings:
  - id: "W_SOURCE_FIELD_MISSING"
    message: "source field is not confirmed yet"
    blocking: false
```

```yaml
violations:
  - id: "V_ARCHIVE_CREATED_BEFORE_APPROVAL"
    rule: "ASSERT.NOT final_archive_created before G_PRE_ARCHIVE_APPROVAL"
    severity: "critical"
```

If a critical violation exists, the Ordo program must not pretend that the result is valid.

## Debug Output for a Person

A complete trace may be long. Ordo should therefore distinguish:

```text
machine trace
human debug summary
```

The machine trace is needed by the runtime, tests, and compiler.

The human debug summary is needed by the user.

For example:

```text
Debug summary:
Path A1 was selected because the input describes a field change in the main source row.
Path A2 was rejected because no related entity was confirmed.
The final archive is blocked because gate G_PRE_ARCHIVE_APPROVAL has not passed.
Next required action: confirm the source field and fixture.
```

This is short, understandable, and does not overload the person with complete JSON.

## Debug Mode and Privacy

A debug trace must not blindly expose all raw data.

A trace may contain confidential payloads, personal data, internal names, or technical details.

Ordo should therefore support trace levels:

```text
trace_level: summary
trace_level: standard
trace_level: full
trace_level: redacted
```

For example:

```yaml
run:
  mode: "debug"
  trace_level: "redacted"
```

In this mode, a trace may show that a field was used while hiding its value:

```yaml
state_diff:
  - field: "tax_id"
    before: "[REDACTED]"
    after: "[REDACTED]"
```

This is important if Ordo is used in real products.

## Execution Mode and Guarantee Level

`Debug mode` explains execution, but by itself it does not guarantee that every gate was actually enforced. Ordo v0.12 therefore adds a separate `execution_mode` field.

```yaml
program: history_event_playbook
execution_mode: full_runtime
```

Base modes:

```text
full_runtime  — runtime or helper runner controls state, node transitions, and hard gates;
chat_internal — the model works in chat and may run scripts or maintain state in session files, but the gate invocation point is not fully enforced;
freeform_only — Ordo discipline is executed through text without external control.
```

Honest guarantee table:

| execution_mode | Who determines when a gate is invoked | Who performs the check | Guarantee level |
|---|---|---|---|
| `full_runtime` | code / runner | code or model under protocol | highest |
| `chat_internal` | model in chat | session code or model | medium |
| `freeform_only` | model | model through text | lowest |

This table is needed so that Ordo's strength is not overstated. In `chat_internal` mode, a mechanical check may genuinely be executed by code, but without an external runtime the model still has to invoke it at the correct time.

## Debug Mode and the Compiler

The Ordo compiler must be able to add trace points automatically.

An Ordo Source author should not have to log every small detail manually.

For example, if Source contains:

```yaml
nodes:
  - id: "NODE_SELECT_PATH"
    branches:
      - path: "A1"
        when: "direct source row change"
      - path: "A2"
        when: "related entity change"
```

the compiler should automatically create trace points in IR:

```json
{
  "op": "PATH.EXPLAIN",
  "node": "NODE_SELECT_PATH",
  "required": true,
  "trace_source": "model_self_report"
}
```

The debug layer must not be an “addition on the side.” It must be part of compilation.

## Debug Mode and Model Errors

A debug trace helps distinguish different classes of problems.

If a result is wrong, the cause may be:

```text
1. incorrect instruction;
2. incomplete contract;
3. ambiguous context;
4. incorrect path selection;
5. skipped gate;
6. incorrect output template;
7. weak FREEFORM;
8. library conflict;
9. model failed to execute IR;
10. user changed the requirement during the process.
```

Without trace, all of these look the same:

```text
the model made a mistake
```

With trace, we can say more precisely:

```text
the error occurred at NODE_SELECT_PATH;
the model selected A1 although the fixture matched A2;
the reason is that the branch condition lacks a rule for a related entity through the Identification Center.
```

This is no longer merely a complaint. It is a diagnosis.

## Typical Mistakes

### Mistake 1. Asking the Model to “Explain” Without Requiring Trace

An explanation after the fact may be elegant but unverifiable.

A structured trace during execution is better.

### Mistake 2. Logging Only the Selected Path

The selected path alone does not show why other paths were rejected.

Rejected paths with reasons must also be logged.

### Mistake 3. Not Logging State Diff

If only the final state is visible, it is difficult to understand exactly where it became incorrect.

A state diff is needed after important nodes.

### Mistake 4. Hiding the Gate Report in Response Text

A gate report must be structured.

Otherwise, it is difficult to test.

### Mistake 5. Showing Too Much Debug Information to a Person

The complete trace is needed by the machine and playbook author.

A debug summary is often sufficient for the user.

### Mistake 6. Confusing Execution Trace with Chain of Thought

Ordo does not need the model's private reasoning text.

Ordo needs a formal execution log: node, path, gate, state, output, evidence.

### Mistake 7. Omitting `trace_source`

A trace without `trace_source` creates the false impression that it is always a runtime log.

In v0.12, it must explicitly show whether it is `model_self_report`, `runtime_enforced`, or `hybrid`.

### Mistake 8. Omitting `execution_mode`

If the execution mode is absent, the reader or next process cannot understand the guarantee level of the trace.

`full_runtime`, `chat_internal`, and `freeform_only` are different control levels, not different names for the same mode.

## Mini-Exercise

Take this simple instruction:

```text
Prepare a package for a new historical event, but do not create the final archive until I confirm the source field and QA scenarios.
```

Describe what should appear in the debug trace.

At minimum, define:

```text
- run_id;
- execution_mode;
- trace_source;
- input snapshot;
- selected path;
- rejected paths;
- state before/after source-field confirmation;
- gate prohibiting archive creation;
- gate status before confirmation;
- warning if QA scenarios are not yet defined;
- human debug summary.
```

Then formulate a violation for the case where the model nevertheless created the archive before confirmation.

## Short Summary

`Debug mode` is an Ordo program execution mode in which the result is accompanied by a structured execution trace.

The execution trace should show:

```text
- run_id;
- execution_mode;
- trace_source;
- input snapshot;
- selected and rejected paths;
- decision log;
- state snapshots;
- state diffs;
- gate report;
- knowledge trace;
- warnings;
- violations;
- human debug summary.
```

The main value of debug mode is that it transforms a problem from:

```text
the model somehow did the wrong thing
```

into:

```text
at this node, this path was selected for this reason; this gate was skipped; this state changed incorrectly; this is where the Ordo program must be fixed.
```

That is why debug mode is not a service feature around Ordo but part of the language itself.

> **M72.1 update.** This chapter explains the debug representation of trace. The full normative core element `EXECUTION_TRACE`, its fields, event catalog, replay, and integrity are described in Chapter 74.
