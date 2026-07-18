# Chapter 34. Minimum Requirements for an Author

## Why This Is Needed

Ordo makes it possible to turn human instructions into a controlled process for an AI model. But this does not mean that any long text automatically becomes a good Ordo program. If the author does not understand what is being described, where the process must stop, which decisions the model may make independently, and which require human confirmation, even the best syntax will not save the instruction.

An Ordo program author does not have to be a programmer in the classical sense. The author may be an analyst, methodologist, product specialist, QA engineer, business expert, or technical writer. But the author must think not only in text, but in processes.

Ordo does not require the author to write Java, Python, or JavaScript. It does require discipline: seeing task structure, distinguishing a rule from an example, an expected result from a preference, a mandatory gate from a recommendation, and a confirmed fact from an assumption.

## An Ordo Program Author Designs Model Behavior

When a person writes an ordinary prompt, they often describe only the desired result:

```text
Prepare an analytical package for a new historical event.
```

For Ordo, this is insufficient. The author must describe not only the result, but also the model's behavior:

```text
- where to begin;
- which data to collect;
- which questions to ask;
- which path options exist;
- what counts as confirmed;
- where the model must stop;
- what is forbidden without approval;
- which outputs to create;
- which gates must pass before handoff;
- which debug/test/improvement records must be supported.
```

An Ordo program author therefore does not simply write an instruction. The author designs a controlled execution process.

## Minimum Requirement 1. Understand the Intent

The author must clearly understand why the Ordo program exists.

Bad:

```text
Help the analyst.
```

Better:

```text
Guide the analyst through guided intake for a new historical event, collect a confirmed contract, determine the path, build a compact package, and execute validation gates before handoff.
```

The intent must be specific enough to verify whether the program fulfilled its purpose.

If the intent is vague, problems follow: the model asks the wrong questions, enters the wrong path, creates the wrong outputs, and does not understand where it must stop.

## Minimum Requirement 2. Distinguish Contract from Context

A common authoring mistake is mixing mandatory conditions with background explanation.

A contract is what the process cannot proceed without.

Context is what helps the model understand the situation better.

For example:

```text
The event concerns a change in company status.
```

This may be context.

But this is a contract:

```text
Before package generation, the following must be confirmed:
- event alias;
- source row;
- source field;
- old/new values;
- path;
- expected output files.
```

The author must explicitly mark what is contract and what is merely explanation. Otherwise, the model may interpret an important condition as optional advice.

## Minimum Requirement 3. Define State

If a process has multiple steps, the author must describe state.

State is process memory: what is already known, what is confirmed, what still awaits a decision, which gates have passed, and which assumptions remain open.

Without state, the model may repeatedly ask about something already confirmed or, conversely, treat something the user merely discussed as confirmed.

Minimum state for a complex Ordo program should contain:

```text
- confirmed facts;
- assumptions;
- selected path;
- pending decisions;
- passed gates;
- blocked gates;
- selected outputs;
- generated artifacts;
- feedback/improvement records.
```

The author does not necessarily need to describe a complete state machine immediately. But the author must at least understand which data the process must remember between steps.

## Minimum Requirement 4. Design Nodes as Questions, Not Chaotic Dialogue

An Ordo program often works as guided intake. This means the model does not merely “talk”; it moves through process nodes.

Each node should have a clear role:

```text
- collect the alias;
- determine the path;
- confirm the source row;
- collect values;
- check the output contract;
- obtain approval;
- perform validation;
- create the handoff.
```

Bad node:

```text
Ask the user for everything necessary.
```

Better node:

```text
NODE.DEF collect_source_field:
  goal: "Confirm the source field whose change creates the event"
  ask: "Which source field is the event trigger?"
  required_answer: true
  updates_state:
    - source_field
  next:
    when confirmed: collect_old_new_values
```

The author must be able to divide a large process into logical nodes.

## Minimum Requirement 5. Define Gates

A gate is a point where the process checks a condition before moving forward.

The author must be able to answer:

```text
Where is the model not allowed to continue without a check?
```

For example:

```text
- do not create the final archive without a self-check;
- do not consider the contract confirmed without explicit confirmation;
- do not generate a code prompt without an agreed output contract;
- do not use a source row unless it has been confirmed;
- do not create a HistoryEvent when the scenario is a no-op.
```

If the author does not define gates, the model acts probabilistically: sometimes correctly, sometimes not.

Ordo exists precisely so that such critical points are described explicitly.

## Minimum Requirement 6. Write Negative Rules

People often describe what the model should do but forget to describe what it must not do.

For Ordo, this is critical.

Positive instructions are not enough:

```text
Create a QA package.
```

Negative instructions are also needed:

```text
ASSERT.NOT:
  - do not create final archive before validation passed
  - do not invent missing source values
  - do not mark assumption as confirmed
  - do not hide mandatory gate inside FREEFORM
```

The author must be able to identify dangerous model actions and prohibit them explicitly.

## Minimum Requirement 7. Define Outputs

An output is not merely an “answer.” In complex processes, an output may be a set of documents, JSON structures, prompts, validation reports, QA packages, or changelog entries.

The author must describe:

```text
- which outputs must be created;
- which outputs are mandatory;
- which outputs are auxiliary;
- which fields or sections must be inside them;
- which outputs cannot be created before approval;
- how to verify that an output is ready.
```

Bad:

```text
Create a package.
```

Better:

```text
OUTPUT.DEF compact_history_event_package:
  required_files:
    - README.md
    - SUMMARY.json
    - VALIDATION_REPORT.json
    - CONSISTENCY_CHECK_REPORT.json
    - 01_HISTORY_EVENT_PASSPORT_<ALIAS>.md
    - 02_JIRA_TASK_<ALIAS>.md
    - 04_IMPLEMENTATION_PROMPT_<ALIAS>.md
    - 05_QA_PACKAGE_<ALIAS>.md
    - 07_PROCESS_IMPROVEMENT_FEEDBACK_<ALIAS>.md
    - 08_QA_AUTOMATION_SPEC_<ALIAS>.yaml
    - 09_QA_AUTOMATION_README_<ALIAS>.md
```

An output must be verifiable.

## Minimum Requirement 8. Keep FREEFORM Under Control

The author should not try to formalize everything. But the author must understand that FREEFORM is not a dumping ground for difficult rules.

FREEFORM may be used for:

```text
- explanations;
- examples;
- domain nuances;
- historical notes;
- text templates;
- complex human wording.
```

But the following must not be hidden in FREEFORM:

```text
- blocking gates;
- required approvals;
- output contracts;
- state transitions;
- status semantics;
- negative assertions.
```

The author must be able to decide what to formalize and what to leave as controlled FREEFORM.

## Minimum Requirement 9. Think About Debugging and Tests from the Beginning

An Ordo program without a debug/test layer quickly becomes difficult to evolve.

At minimum, the author should define:

```text
- which paths need testing;
- which gates are critical;
- which scenarios must be no-op;
- which errors have already occurred;
- which regression tests are needed;
- which debug logs are needed to explain a decision.
```

This does not mean that every small Ordo program needs a large test suite. But tests should be mandatory for playbooks, Domain Packs, and libraries.

## Minimum Requirement 10. Capture Improvement Feedback

An Ordo program author must expect real-world use to reveal problems.

A user may say:

```text
- this question should be asked earlier;
- a gate is needed here;
- this rule did not work;
- this should be moved into a library;
- this needs a regression test;
- this FREEFORM should be formalized.
```

All such comments should become improvement records instead of disappearing in chat.

The author should maintain the cycle:

```text
feedback → issue record → affected unit → patch suggestion → test suggestion → approval → regression
```

This is how an Ordo program improves after real use.

## What the Author Does Not Need to Know

An Ordo program author does not have to:

```text
- be a backend developer;
- write a compiler;
- know every IR opcode;
- create a perfect structure immediately;
- formalize 100% of domain logic;
- write a complex runner.
```

But the author must be able to:

```text
- see the process;
- distinguish a rule from an example;
- define stopping points;
- describe expected behavior;
- capture state;
- verify outputs;
- accept feedback and turn it into improvements.
```

## Typical Authoring Mistakes

### Mistake 1. Writing Ordo as a Long Prompt

If a document is merely a large block of text without nodes, gates, state, and outputs, it is not yet an Ordo program.

### Mistake 2. Failing to Define Who Makes the Decision

The model may help, but it is not allowed to make every decision independently.

The author must explicitly specify:

```text
- model_decision;
- user_approval;
- analyst_decision;
- blocked_until_confirmed.
```

### Mistake 3. Failing to Describe Negative Scenarios

If only successful scenarios are described, the model may behave incorrectly in edge cases.

### Mistake 4. Making FREEFORM Too Large

Large FREEFORM without coverage is a return to the large-prompt approach.

### Mistake 5. Failing to Plan for Evolution

An Ordo program will almost always change. Without improvement records, a changelog, and regression tests, every change becomes a risk.

## Mini-Exercise

Take any complex prompt you have used before and answer these questions:

```text
1. What is the intent of this prompt?
2. Which contract must be confirmed before execution?
3. Which state must be remembered?
4. Which nodes can be identified?
5. Where are gates needed?
6. Which ASSERT.NOT rules are needed?
7. Which output must be created?
8. What can remain in FREEFORM?
9. Which single debug trace would help explain an error?
10. Which single regression test should be added?
```

If you can answer these questions, you are already thinking like an Ordo program author.

## Short Summary

An Ordo program author is not simply someone who writes instructions for AI. The author designs controlled model behavior.

Minimum requirements for an author:

```text
- understand intent;
- distinguish contract from context;
- describe state;
- build nodes;
- define gates;
- write ASSERT.NOT;
- define the output contract;
- control FREEFORM;
- think about debugging and tests;
- capture improvement feedback.
```

Ordo does not require the author to be a programmer. But it does require thinking in processes, checks, and instruction evolution.

---
