# Chapter 16. Tests, Fixtures, and Expected Behavior

## Why This Is Needed

When we work with ordinary code, we almost never consider a program ready merely because it worked correctly once by hand. We write tests, check different scenarios, record expected behavior, and rerun those checks after changes.

Instructions for AI models are often handled less rigorously. An instruction is rewritten and works better in one case but silently breaks another. A new rule is added and the model starts asking questions in the wrong order. A gate is strengthened and the model can no longer reach the result. A gate is weakened and the model starts creating the final artifact before confirmation.

Without tests, these problems are discovered only by accident. If the playbook is large, finding the cause becomes very difficult.

An Ordo program should therefore be tested not only by its final text but by process behavior.

![Nebu — idea: a test checks process behavior](../assets/mascots/64x64/Nebu_idea_64x64.png)

An Ordo test asks not only:

```text
is the final output correct?
```

It asks a broader question:

```text
did the process proceed exactly as it was supposed to?
```

In v0.12 this becomes even more important because Ordo explicitly distinguishes trust classes: mechanical checks, semantic model checks, repeated checks, and human decisions. A test must see this difference rather than merely say “the gate passed.”

---

## Simple Explanation

In a normal prompt-based approach, testing often looks like this:

```text
I gave the model input data.
The model answered something.
The answer seems fine.
```

That is insufficient for Ordo.

![Nebu — attention: test more than the final output](../assets/mascots/64x64/Nebu_attention_64x64.png)

Ordo should check:

```text
- which path was selected;
- which paths were rejected;
- which questions the model asked;
- which questions the model was not allowed to ask;
- how unmatched input was handled;
- which state changed;
- which gates passed;
- which methods were used to check gates;
- which trust_class each gate had;
- which gates blocked execution;
- whether forbidden output was created;
- whether a no-op scenario was handled correctly;
- whether FREEFORM was used invisibly;
- whether an action occurred without approval;
- whether behavior matches the declared execution_mode;
- whether an ASSERTION was violated.
```

An Ordo program test is therefore a test of execution behavior.

---

## Fixture: Controlled Input

A repeatable test needs a fixture.

A fixture is a prepared set of input data for a test.

In ordinary code, a fixture may be a test object, database record, or file. In Ordo, a fixture may contain:

```text
- user message;
- initial state;
- available context;
- execution_mode;
- control_level;
- connected libraries;
- active profile;
- domain pack;
- source documents;
- expected user confirmations;
- environment constraints;
- previous trace if the test is replay-based.
```

Example:

```yaml
fixture:
  id: "FX_HISTORY_EVENT_A1_BASIC"
  execution_mode: "chat_internal"
  control_level: "standard"
  user_message: "We are creating a historical event for a company status change."
  initial_state:
    event_alias: null
    source_field: null
    contract_confirmed: false
  context:
    domain_pack: "history_event"
    available_paths:
      - "A1"
      - "A2"
      - "A4"
```

A fixture lets us repeat the same scenario and obtain a comparable result.

---

## Expected Behavior: What Exactly Should Happen

Ordinary tests often check only the result. For example:

```text
expect file package.zip
```

That is not enough in Ordo. Expected behavior must be described.

Expected behavior is the contract for how the process is supposed to behave.

It may include:

```text
- expected path;
- expected node sequence;
- expected questions;
- expected state;
- expected gates;
- expected gate methods;
- expected trust classes;
- expected assertions;
- expected output;
- expected block;
- expected no-op;
- expected warnings;
- expected trace_source;
- expected absence of forbidden actions.
```

Example:

```yaml
expected:
  path:
    selected: "A1"

  questions:
    required:
      - intent: "request_event_alias_confirmation"
      - intent: "request_source_field_confirmation"
    forbidden:
      - intent: "request_final_archive_generation"

  gates:
    - id: "domain_pack.history_event.G_CONTRACT_CONFIRMED"
      method: "human"
      trust_class: "human_decision"
      status: "blocked"

  output:
    final_archive_created: false
```

Importantly, the test does not require the model to repeat exact wording. It checks semantic behavior.

---

## TEST.DEF

In Ordo, a test can be described with `TEST.DEF`.

Simplified:

```yaml
TEST.DEF:
  id: "TC_NO_FINAL_OUTPUT_BEFORE_APPROVAL"
  title: "Do not create final output before approval"
  mode: "test"

  fixture:
    execution_mode: "chat_internal"
    user_message: "Create the final archive immediately."
    initial_state:
      approval:
        pre_archive: false

  expected:
    gates:
      - id: "domain_pack.history_event.G_PRE_ARCHIVE_APPROVAL"
        method: "human"
        trust_class: "human_decision"
        status: "blocked"

    assertions:
      - id: "domain_pack.history_event.A_NO_ARCHIVE_BEFORE_APPROVAL"
        polarity: "not"
        status: "passed"

    output:
      final_archive_created: false

    not_allowed:
      - "archive.generate"
      - "handoff.mark_ready"
```

This test says that even if the user asks for the final archive immediately, the Ordo program must not cross a blocking gate without approval.

---

## ASSERTION in Tests

In v0.12, `ASSERTION` becomes the canonical way to describe a required or forbidden condition.

`ASSERT.NOT`, a `negative gate`, and `EXPECT.NOT` should no longer be three separate rules maintained manually by the author. They are different projections of one assertion.

For example:

```yaml
ASSERTION.DEF:
  id: "domain_pack.history_event.A_NO_INVENTED_ALIAS"
  polarity: "not"
  condition: "alias_created_without_user_confirmation"
  phase:
    - runtime
    - test
  severity: "block"
  on_fail: "STOP"
```

The compiler expands this rule into a runtime check:

```yaml
ASSERT.NOT:
  id: "domain_pack.history_event.A_NO_INVENTED_ALIAS"
  condition: "alias_created_without_user_confirmation"
  on_fail: "STOP"
```

and a test-time expectation:

```yaml
EXPECT.NOT:
  id: "domain_pack.history_event.A_NO_INVENTED_ALIAS"
  condition: "alias_created_without_user_confirmation"
```

This protects against a common mistake: a rule exists in the playbook but was forgotten in the regression suite.

---

## EXPECT.PATH

`EXPECT.PATH` checks which path should be selected.

For example:

```yaml
EXPECT.PATH:
  selected: "A1"
  rejected:
    - id: "A2"
      reason_required: true
    - id: "A4"
      reason_required: true
```

This matters for a decision tree. If the model produces the correct output through the wrong path, that is still a problem. In a complex process, the wrong path may later break gates, state, or QA.

---

## EXPECT.GATE

`EXPECT.GATE` checks gate behavior.

In v0.12, a test should check not only `status` but also `method` and `trust_class`.

```yaml
EXPECT.GATE:
  - id: "domain_pack.history_event.G_SOURCE_FIELD_CONFIRMED"
    method: "human"
    trust_class: "human_decision"
    status: "blocked"
    because: "source field has not been confirmed by user"
```

This test protects against a model “filling in” a missing confirmation by itself.

This is critical for Ordo. If a gate exists in documentation but does not block execution, it is not a gate; it is decorative text.

---

## EXPECT.STATE

`EXPECT.STATE` checks how state changes.

```yaml
EXPECT.STATE:
  after_node: "N_COLLECT_ALIAS"
  values:
    event_alias: "LU_CHANGE_STATUS"
    contract_confirmed: false
```

State tests are needed because many errors occur before final output: the model remembered a decision incorrectly, confused `confirmed` with `assumed`, or copied a value from an example into a real contract.

---

## EXPECT.OUTPUT

`EXPECT.OUTPUT` checks the result, but in Ordo a result is not necessarily text.

Output may be:

```text
- document;
- JSON;
- archive;
- checklist;
- question;
- blocked status;
- handoff;
- validation report;
- improvement record.
```

Example:

```yaml
EXPECT.OUTPUT:
  type: "question"
  must_request:
    - "source_field"
    - "old_value"
    - "new_value"
  must_not_create:
    - "final_package"
```

This means the correct output at this stage is not a final document but a question to the user.

---

## EXPECT.NOOP

No-op scenarios are very important.

A no-op is a situation where correct behavior is to create nothing or change nothing.

![Nebu — thinking: no-op is also expected behavior](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Classic instructions often fail here because the model assumes it must “do something.” In real processes, however, the correct response is sometimes:

```text
change nothing;
create no event;
generate no ChangeRecord;
create no archive;
stop the process.
```

Example:

```yaml
TEST.DEF:
  id: "TC_EXPECTED_NO_CHANGE"
  title: "Do not create an event if the value did not change"

  fixture:
    old_value: "active"
    new_value: "active"

  expected:
    noop: true
    no_new_change_record: true
    no_history_event_created: true
```

No-op tests protect the system from unnecessary activity.

---

## EXPECT.NOT

`EXPECT.NOT` remains a useful name for a test expectation, but in v0.12 it should be a projection of `ASSERTION`, not a separate rule.

For example:

```yaml
EXPECT.NOT:
  - assertion_id: "domain_pack.history_event.A_NO_FINAL_ARCHIVE_BEFORE_APPROVAL"
  - assertion_id: "domain_pack.history_event.A_NO_INVENTED_SOURCE_ROW"
  - assertion_id: "domain_pack.history_event.A_NO_ASSUMPTION_AS_CONFIRMED"
  - assertion_id: "core.assertions.A_NO_HIDDEN_GATE_INSIDE_FREEFORM"
```

This lets us test not only what the model must do but also what it must not do.

---

## EXPECT.CLARIFY

In v0.12, `NODE.DEF` gains a controlled escape hatch: `on_unmatched_input`. A test must therefore be able to check not only normal `allowed_answers` but also a user response that does not fit the tree.

```yaml
EXPECT.CLARIFY:
  node: "domain_pack.history_event.N_EVENT_KIND"
  when_input: "do it like last time"
  expected_action: "CLARIFY.REQUEST"
  strategy: "rephrase_and_narrow"
  max_attempts: 2
  on_exhausted: "escalate_to_human"
```

This test protects against uncontrolled improvisation: the model must not invent a new path if the input matches none of the allowed answers.

---

## Test Behavior, Not Response Style

One mistake is testing an Ordo program as a text template.

Bad:

```text
The model must write exactly: "Confirm the event alias."
```

Better:

```yaml
expected:
  question_intent:
    - "request_event_alias_confirmation"
```

We test the semantic action, not the literal wording.

This matters because an AI model may phrase a question differently while executing the same Ordo step.

---

## Tests as Protection Against Instruction Degradation

As an Ordo program evolves, tests protect it against accidental degradation.

For example, we add a new library:

```yaml
include:
  - library: "ordo.artifact.validation"
    version: "0.1"
```

After that, we should verify that old scenarios still work:

```text
- Path A1 is still selected correctly.
- The pre-archive gate is still blocking.
- The gate has the correct method.
- A self_verification gate is not presented as a mechanical gate.
- FREEFORM has not started overriding structured rules.
- No-op scenarios do not create unnecessary events.
- ASSERTION expands into runtime and test checks.
```

Without tests, the problem will appear only during real work.

---

## Typical Mistakes

### Mistake 1. Testing Only the Final Document

A correct-looking final document does not prove the process was correct. The model may have skipped approval or invented part of state.

### Mistake 2. Not Testing Blocking Gates

A gate without a test can easily become a recommendation.

### Mistake 3. Not Testing `method` and `trust_class`

In v0.12, a test must see whether a gate was mechanical, model-based, or human. Otherwise a semantic self-check may accidentally look like deterministic verification.

### Mistake 4. Not Testing No-Op

If no-op behavior is not tested, the system will almost certainly begin creating unnecessary results.

### Mistake 5. Testing Only the Happy Path / Main Successful Scenario

Complex Ordo programs must also test failures, stops, incomplete data, conflicts, unmatched input, and incorrect user requests.

### Mistake 6. Not Binding a Test to a Node, Gate, Path, or Assertion

If a test fails but it is unclear which program element it checks, debugging becomes much harder.

### Mistake 7. Keeping `EXPECT.NOT` Separate from `ASSERTION`

If a negative rule is described separately at runtime and in tests, the two will eventually drift. In v0.12, `ASSERTION` should be the source and `EXPECT.NOT` its test projection.

---

## Mini-Exercise

Take this simple instruction:

```text
Prepare a response to a customer about a delivery delay.
```

Describe one Ordo test case:

```text
1. What is the fixture?
2. What is the execution_mode?
3. What is the expected path?
4. Which questions should the model ask?
5. Which gate should block the final response?
6. What method and trust_class should that gate have?
7. Which ASSERTION prohibits inventing the reason for the delay?
8. Which output is forbidden before confirmation?
9. What no-op scenario is possible?
```

For example, a no-op may be this: if the user asks to answer the customer but provides no information about the reason for the delay, the model must not invent a reason. It must stop and request context.

---

## Short Summary

An Ordo test is not a check of beautiful text. It is a check of process behavior.

A test should record:

```text
input → fixture → expected path → expected state → expected gates → expected assertions → expected output → forbidden actions
```

In v0.12, a test should also see:

```text
execution_mode → gate.method → trust_class → trace_source → assertion projections
```

This is what makes it possible to evolve complex instructions without chaos.

Without tests, an Ordo program gradually turns back into a large prompt that is difficult to change and almost impossible to debug reliably.

---

<!-- REVIEWED: chapter 16; updated for Ordo v0.12 ASSERTION/test projections; Nebu markers checked -->
