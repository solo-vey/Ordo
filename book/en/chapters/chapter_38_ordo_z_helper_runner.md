# Chapter 38. Ordo with a Helper Runner

## Why a Helper Runner Is Needed

In the previous chapter, we examined the simplest way to use Ordo: without a separate runtime, where the model reads Ordo Source or Semantic JSON IR itself and attempts to follow the rules in a disciplined way.

This mode is useful for getting started. But complex processes quickly expose its limits.

The model may forget a gate. It may implicitly change state. It may skip a node. It may say that a check passed even though the trace contains no evidence. It may fail to create an improvement record even when the user explicitly points out a problem.

This is where an intermediate level appears:

```text
Ordo with a helper runner
```

A helper runner is not a complete “intelligent model” and is not a replacement for an LLM. It is an auxiliary execution layer that takes responsibility for process control.

Its task is simple:

```text
the model thinks and produces content,
the runner controls order, state, gates, tests, and trace.
```

![Nebu — idea](../assets/mascots/64x64/Nebu_idea_64x64.png)

In other words, a helper runner turns Ordo from a structured instruction for a model into an executable process with external control.

## Simple Explanation

You can imagine Ordo without a runtime as a cook who reads a recipe and decides independently whether everything was done correctly.

Ordo with a helper runner is more like a kitchen with a process sheet, checkpoints, an action log, and quality control.

The cook still prepares the dish. But the system ensures that the cook:

```text
- does not skip a mandatory step;
- does not serve the dish before inspection;
- does not replace an ingredient without permission;
- records what was done;
- explains why a particular path was selected.
```

In Ordo, this means:

```text
- the runner stores state;
- the runner determines the current node;
- the runner blocks transitions through blocking gates;
- the runner gives the model only the relevant instruction fragment;
- the runner captures trace;
- the runner runs tests;
- the runner builds the gate report;
- the runner collects feedback records.
```

The model remains the semantic executor. The runner becomes the process controller.

## What Exactly the Helper Runner Does

A helper runner can perform several roles.

### 1. Loading the Ordo Program

The runner reads Ordo Source or compiled IR.

For example:

```text
- the main Ordo program;
- included libraries;
- the selected Profile;
- the selected Domain Pack;
- templates;
- gates;
- tests;
- the FREEFORM ledger.
```

It does not rely on the model to read an entire long document correctly. The runner itself determines which parts are needed for the current step.

### 2. State Control

The runner stores state outside the model.

This is very important. If state exists only in the conversation context, it can easily be lost or changed without notice.

In runner-based mode, state may be a separate JSON object:

```json
{
  "run_id": "RUN-001",
  "current_node": "NODE_COLLECT_CONTRACT",
  "confirmed": {
    "alias": true,
    "source_field": false
  },
  "outputs": {
    "final_package_created": false
  },
  "gates": {
    "G_CONTRACT_CONFIRMED": "blocked"
  }
}
```

The model is not allowed simply to declare that state has changed. It must propose a change, and the runner must apply or reject it.

### 3. Transition Control

The runner checks whether a transition from one node to another is allowed.

For example, the model wants to move to package generation. The runner checks:

```text
Has the contract been confirmed?
Have the approval gates passed?
Is the source row available?
Has the self-check been completed?
Are there any ASSERT.NOT violations?
```

If not, the runner blocks the transition.

This is fundamentally different from an ordinary prompt. In a prompt, the model “must remember” that it cannot proceed. In runner-based Ordo, the transition is technically disallowed.

![Nebu — attention](../assets/mascots/64x64/Nebu_attention_64x64.png)

### 4. Building a Task for the Model

The runner does not necessarily give the model the entire Ordo program.

It may provide only the current execution slice:

```yaml
model_task:
  current_node: "NODE_SOURCE_FIELD_CONFIRMATION"
  allowed_actions:
    - "ask_one_question"
    - "update_state_proposal"
  forbidden_actions:
    - "generate_final_package"
    - "mark_contract_confirmed_without_user_answer"
  context:
    known:
      alias: "LU_CHANGE_STATUS"
    missing:
      - "source_field"
  expected_output:
    type: "question"
```

This reduces the risk that the model becomes confused by a long playbook.

### 5. Gate Enforcement

The runner can make gates real blockers.

For example:

```yaml
gate:
  id: "G_PRE_ARCHIVE_APPROVAL"
  method: human
  trust_class: human_decision
  type: "blocking"
  condition:
    user_approved_archive_generation: true
```

If the condition is not satisfied, the runner does not allow the action:

```text
generate_archive
```

Even if the model attempts to perform it.

### 6. Trace and Audit

The runner can capture a complete trace independently of how disciplined the model is in describing it.

The trace should contain:

```text
- input;
- current node;
- selected path;
- rejected paths;
- state before;
- state after;
- gates;
- model proposals;
- runner decisions;
- warnings;
- violations;
- final outputs.
```

This makes the process auditable.

### 7. Test Execution

The runner can execute `TEST.DEF`.

For example:

```text
take fixture →
run the Ordo program →
check expected path →
check expected gates →
check forbidden output →
build report.
```

This is much closer to conventional software testing.

### 8. Improvement Capture

The runner can automatically collect user comments and turn them into `IMPROVEMENT.RECORD`.

For example, if the user says:

```text
You should have asked for the source field earlier here.
```

The runner can bind this feedback to:

```text
- run_id;
- node;
- path;
- gate;
- instruction fragment;
- Domain Pack;
- library version.
```

It can then propose a patch and a regression test.

## Ordo Construct

In Source format, helper-runner mode may look like this:

```yaml
execution:
  mode: "normal"
  runtime:
    type: "helper_runner"
    responsibilities:
      - "state_management"
      - "node_routing"
      - "gate_enforcement"
      - "trace_capture"
      - "test_execution"
      - "feedback_capture"

state:
  storage: "external"
  format: "semantic_json"

gates:
  enforcement: "runner_blocking"

trace:
  trace_source: "model_self_report"
  required: true
  level: "decision"

model:
  role: "semantic_executor"
  allowed_to:
    - "interpret_context"
    - "propose_state_update"
    - "generate_candidate_output"
    - "explain_reasoning_summary"
  not_allowed_to:
    - "override_blocking_gate"
    - "silently_change_state"
    - "skip_required_node"
```

In compiled IR, this may be represented as a set of operations:

```json
[
  {
    "op": "RUNTIME.DEF",
    "runtime": "helper_runner",
    "responsibilities": [
      "state_management",
      "gate_enforcement",
      "trace_capture"
    ]
  },
  {
    "op": "STATE.EXTERNAL",
    "format": "semantic_json"
  },
  {
    "op": "GATE.ENFORCE",
    "mode": "runner_blocking"
  },
  {
    "op": "MODEL.ROLE",
    "role": "semantic_executor"
  }
]
```

## An Important Responsibility Boundary

A helper runner must not pretend that it understands the full meaning of the domain task by itself.

For example, in the History Event Playbook, the runner may know:

```text
- which paths exist;
- which gates must be passed;
- which fields are mandatory;
- which output cannot be created before approval;
- which tests must be run.
```

But the model is still needed for:

```text
- explaining business meaning;
- producing human-readable text;
- analyzing ambiguous wording;
- proposing names;
- creating documentation;
- summarizing feedback.
```

The runner does not replace the model. It constrains and organizes the model's work.

![Nebu — thinking](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## Small Example

Without a helper runner, the user writes:

```text
Create a new historical event.
```

The model must remember the entire playbook, choose a path, ask questions, avoid proceeding too early, and avoid creating the package before the proper time.

With a helper runner, the process looks different.

The runner creates a run:

```json
{
  "run_id": "RUN-100",
  "current_node": "ENTRY_START",
  "state": {},
  "allowed_actions": ["classify_input", "ask_entry_question"]
}
```

The model proposes:

```json
{
  "proposed_action": "ask_question",
  "question": "What type of change needs to be converted into a historical event?"
}
```

The runner verifies that this is an allowed action and sends the question to the user.

The user then answers. The runner updates state. The model proposes a path. The runner checks the gates. Only then does the process move forward.

As a result, the model does not “hold the entire process in its head.” It works step by step within boundaries controlled by the runner.

## How a Helper Runner Differs from Native Ordo

A helper runner is an intermediate level.

The model does not yet support Ordo natively. It has no internal Ordo execution engine. But an external runner helps it execute the Ordo program correctly.

Native Ordo would mean that the model itself can:

```text
- understand Ordo IR;
- execute gates;
- maintain state;
- return trace;
- work with tests;
- support libraries;
- explain decisions in a standard format.
```

A helper runner performs part of this work externally.

So we can say:

```text
Ordo without a runtime is a disciplined prompt-based mode.
Ordo with a helper runner is a controlled execution-assisted mode.
Native Ordo is a model that supports Ordo as an execution language itself.
```

## When a Helper Runner Is Especially Needed

A helper runner is needed when:

```text
- the process has many nodes;
- gates must be blocking;
- there are many state transitions;
- regression tests exist;
- libraries must be included;
- Domain Packs must be versioned;
- an audit trail is required;
- there are production outputs;
- mistakes can be expensive;
- several people or models work with one playbook.
```

It is especially useful for playbooks that gradually grow too large to execute reliably through a single long prompt.

## Typical Mistakes

The first mistake is assuming that a helper runner must be very complex from the first version.

It does not. A minimal runner may do only a few things:

```text
- store state;
- know the current node;
- block critical gates;
- write trace;
- run simple tests.
```

That alone is enough to significantly improve controllability.

The second mistake is giving the runner semantic decisions that should belong to the model or a person.

The runner must not invent business meaning. It must control the process.

The third mistake is allowing the model to change state directly.

A better pattern is:

```text
the model proposes a state update;
the runner checks it;
the runner applies or rejects it.
```

The fourth mistake is not logging rejected actions.

If the model attempts to cross a gate, the runner should record this in the trace. Otherwise, it will be unclear why the process was blocked.

The fifth mistake is failing to connect the runner to the improvement loop.

If the runner observes a recurring problem, it should become an issue or improvement record.

## Mini-Exercise

Imagine that you have an Ordo playbook for preparing an analytical package.

Describe a minimal helper runner for it.

Specify:

```text
- which state it must store;
- which gates it must block;
- which model actions are allowed;
- which model actions are forbidden;
- which trace must be written;
- which tests must be run;
- which user feedback should become improvement records.
```

Then ask yourself:

```text
Which part of the process should remain with the model?
Which part should be controlled by the runner?
Which part should require human confirmation?
```

## Short Summary

Ordo with a helper runner is a practical middle level between prompt-based usage and native Ordo support in models.

In this mode, the model remains the semantic executor, while the runner controls state, paths, gates, trace, tests, and feedback records.

This sharply improves the reliability of complex Ordo programs, especially where it is important not merely to obtain an answer, but to prove that the process was executed correctly, validated, and left ready for further improvement.

---
