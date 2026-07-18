# Chapter 18. Feedback & Improvement Loop

## Why This Is Needed

When people work with large instructions for AI models, the first version almost never works perfectly from the start.

The process usually looks different.

First, we write an instruction. Then the model executes it almost correctly but skips an important step. We add a clarification. It stops skipping that step but starts making a mistake somewhere else. We add another rule. The instruction becomes longer and more complex, with exceptions, repetitions, and hidden contradictions. After some time, it becomes difficult to understand where exactly something should be fixed.

In real work, the user constantly provides feedback:

```text
you skipped the self-check;
this should have been asked earlier;
you were not allowed to create the final package here;
this rule should be a gate, not a recommendation;
this should be moved into the playbook;
a no-op test is needed here;
this case should be retained for future tasks;
this improvement should be added to the instruction, not merely considered once.
```

If such observations remain only in chat, they are quickly lost. The model may account for them in the current response, but the next version of the playbook, library, or domain pack may never receive the improvement.

Ordo therefore needs a separate mechanism: not only to execute instructions, debug them, and test them, but also to collect real usage experience and transform it into structured improvement records.

This mechanism is called:

```text
Feedback & Improvement Loop
```

---

## Simple Explanation

The `Feedback & Improvement Loop` is the improvement cycle of an Ordo program.

Its purpose is to transform a human observation into a structured record:

```text
the user notices a problem
→ Ordo captures feedback
→ classifies the problem
→ finds the affected unit
→ proposes a patch
→ proposes a test
→ waits for human approval
→ after confirmation, the change enters the playbook/library/domain pack/compiler
→ the regression suite verifies that nothing was broken
```

This is a major difference from the ordinary prompt approach.

In a prompt-based approach, feedback often looks like this:

```text
Okay, remember this for the future.
```

But what exactly should be remembered? Where? In which file? In which rule? Is this a new gate? A new test? A clarification to FREEFORM? A domain-pack change? A compiler defect?

Ordo should not leave this unclear.

In Ordo, feedback must become an artifact.

![Nebu — idea: feedback must become an artifact](../assets/mascots/64x64/Nebu_idea_64x64.png)

---

## How Feedback Differs from Debug and Testing

Debug answers:

```text
Why did the process proceed this way?
```

Testing answers:

```text
Does the process behave as expected?
```

The Feedback & Improvement Loop answers a different question:

```text
What should be changed in the Ordo program so it works better in the future?
```

These three layers are connected but are not the same.

Debug may show that the model skipped a gate.

A test may show that a scenario failed.

Feedback may record that this was not a random error but a defect in the instruction itself: the gate was described as a recommendation instead of being defined as blocking.

---

## Ordo Construct

The Ordo language needs separate constructs for this layer.

A base set may look like this:

```text
FEEDBACK.CAPTURE
ISSUE.RECORD
IMPROVEMENT.RECORD
PROBLEM.CLASSIFY
ROOT_CAUSE.LINK
AFFECTED.UNIT
PATCH.SUGGEST
TEST.SUGGEST
REGRESSION.ADD
VERSION.NOTE
CHANGELOG.UPDATE
LESSON.LEARNED
```

These names should not be treated as final syntax. The important idea is that feedback must not remain a textual note; it should become part of the executable development system around an Ordo program.

---

## What Is an Improvement Record

An `improvement record` is a structured record of a problem or improvement.

It should contain not only the feedback text but also its context:

```text
- who or what detected the problem;
- in which run it occurred;
- which path was active;
- which node or gate was related to the problem;
- what type of problem it was;
- how critical it was;
- which part of the Ordo program should change;
- which patch is proposed;
- which test should be added;
- whether human approval is required;
- whether the change was added to the changelog.
```

Example:

```yaml
improvement_record:
  id: "IR-2026-07-05-001"

  source:
    type: "user_feedback"
    message: "You skipped the self-check before the archive again."

  classification:
    type: "missed_required_gate"
    severity: "high"

  affected_unit:
    kind: "gate"
    id: "G_PACKAGE_SELF_CHECK"
    owner:
      layer: "domain_pack"
      name: "history_event"

  observed_in:
    run_id: "RUN-2026-07-05-001"
    path: "package_generation"
    node: "final_archive"

  root_cause_hypothesis:
    - "gate exists in documentation but is not enforced as blocking"
    - "archive generation was allowed before validation report"

  proposed_patch:
    - "mark G_PACKAGE_SELF_CHECK as blocking"
    - "add ASSERT.NOT final_archive_created before self_check_passed"

  suggested_tests:
    - id: "TC_NO_ARCHIVE_WITHOUT_SELF_CHECK"
      expected:
        final_archive_created: false
        blocked_gate: "G_PACKAGE_SELF_CHECK"

  approval:
    required: true
    status: "pending"
```

This record can already serve as the basis for a real playbook change.

---

## Affected Unit

One of the most important elements of the improvement loop is `affected_unit`.

A user may say:

```text
Something is wrong here.
```

But that is not enough to evolve Ordo. We need to understand where the problem actually lives.

The problem may be in:

```text
- a specific NODE;
- a specific GATE;
- a status;
- ASSERT.NOT;
- an output contract;
- a FREEFORM block;
- a library;
- a domain pack;
- a profile;
- a compiler rule;
- documentation runtime;
- rendered artifact validation;
- a test fixture;
- the playbook structure itself.
```

An improvement record should therefore always try to bind the problem to a concrete unit.

Example:

```yaml
affected_unit:
  kind: "library"
  id: "ordo.validation.contract_first"
  version: "0.1"
  export: "G_CONTRACT_CONFIRMED"
```

Or:

```yaml
affected_unit:
  kind: "freeform"
  id: "FF_DOMAIN_EDGE_CASES"
  owner:
    layer: "domain_pack"
    name: "history_event"
```

This allows the system to improve the correct location rather than merely patch one scenario.

---

## Problem Classification

Feedback should be classified.

Otherwise, every observation becomes part of a chaotic list.

Typical problem classes include:

```text
missed_required_gate
wrong_path_selected
premature_output
missing_question
wrong_question_order
state_not_updated
state_updated_without_confirmation
implicit_assumption
freeform_overuse
conflicting_rules
library_conflict
missing_test
missing_noop_test
missing_coverage
rendered_artifact_not_validated
compiler_mapping_error
unclear_status_semantics
```

Classification helps determine what kind of change is needed.

For example, if the problem is `missing_question`, `NODE.DEF` may need to change.

If it is `premature_output`, a blocking gate or `ASSERT.NOT` may be needed.

If it is `freeform_overuse`, part of FREEFORM may need to be formalized.

If it is `missing_noop_test`, a test case should be added.

---

## Human Approval

The feedback loop must not automatically rewrite an Ordo program.

This is a very important rule.

![Nebu — attention: feedback is not applied without approval](../assets/mascots/64x64/Nebu_attention_64x64.png)

Ordo may:

```text
- capture the problem;
- propose a root cause;
- propose a patch;
- propose a regression test;
- show the affected unit;
- prepare a changelog note.
```

But applying the change must remain controlled.

The correct cycle is:

```text
feedback captured
→ problem classified
→ affected unit linked
→ patch suggested
→ test suggested
→ human approval required
→ change applied
→ regression suite executed
→ version note / changelog updated
```

Without confirmation, the change should remain in the status:

```text
pending_improvement
```

This protects Ordo from chaotic self-modification.

---

## Connection to the Regression Suite

Every serious observation should result not only in a patch but also in a test.

Bad:

```text
We added to the instruction: do not skip the self-check.
```

Better:

```text
We added blocking gate G_PACKAGE_SELF_CHECK.
```

Even better:

```text
We added blocking gate G_PACKAGE_SELF_CHECK
and regression test TC_NO_ARCHIVE_WITHOUT_SELF_CHECK.
```

Otherwise, the same problem may return after several changes.

Ordo should therefore have a rule:

```text
Every high-severity improvement record should propose at least one regression test.
```

---

## Connection to the Changelog

If feedback leads to an Ordo-program change, that change should appear in the changelog or version note.

For example:

```yaml
version_note:
  version: "0.11.1"
  changes:
    - type: "gate_enforcement"
      description: "G_PACKAGE_SELF_CHECK is now blocking before final archive generation."
      source_improvement_record: "IR-2026-07-05-001"
      regression_tests_added:
        - "TC_NO_ARCHIVE_WITHOUT_SELF_CHECK"
```

This makes it possible to see why a particular change appeared.

Without this, a playbook gradually becomes a set of rules whose history and rationale are no longer understood.

---

## Connection to Libraries

When Ordo has a library mechanism, the feedback loop must work with libraries as well.

The problem may be in an included library rather than in the main playbook.

For example:

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
    as: "contract_first"
```

If a gate from this library behaves incorrectly or does not cover a required case, the improvement record should identify the library itself:

```yaml
affected_unit:
  kind: "library"
  id: "ordo.validation.contract_first"
  version: "0.1"
  export: "G_CONTRACT_CONFIRMED"
```

The improvement can then be applied not only to one playbook but to a reusable solution used by other Ordo programs.

---

## Connection to FREEFORM

FREEFORM will often be a source of difficult problems.

That is normal. FREEFORM exists precisely because not everything can be formalized immediately.

But if a particular FREEFORM block repeatedly causes errors, Ordo should be able to see that pattern.

For example:

```yaml
freeform_feedback:
  freeform_id: "FF_DOMAIN_EDGE_CASES"
  records:
    - "IR-2026-07-05-004"
    - "IR-2026-07-05-009"
  suggested_action:
    - "split freeform block"
    - "formalize recurring rule as GATE.DEF"
    - "add example-based tests"
```

The feedback loop therefore helps gradually reduce the uncontrolled part of an instruction.

![Nebu — thinking: recurring feedback may show that FREEFORM should be formalized](../assets/mascots/64x64/Nebu_thinking_64x64.png)

FREEFORM does not need to disappear completely. But we need to see where it becomes a risk.

---

## Typical Mistakes

### 1. Simply Saying “Remember This for the Future”

This is weak.

In Ordo, we need not only to remember but also to record:

```text
what exactly;
where exactly;
why;
which patch;
which test;
which status.
```

### 2. Applying Changes Without a Regression Test

This quickly creates new problems.

Every serious fix should produce a test.

### 3. Failing to Bind the Problem to an Affected Unit

Without an affected unit, it is unclear what should actually be changed.

### 4. Automatically Applying Every Observation

Feedback does not always imply the correct change. Sometimes the user describes a symptom while the root cause is elsewhere.

Human approval is therefore required.

### 5. Mixing Feedback with the Debug Log

A debug log shows what happened.

A feedback record shows what should be done about it.

---

## Mini-Exercise

Take one real observation about any instruction.

For example:

```text
The model created the final document too early.
```

Try to describe it as an improvement record:

```text
1. What is the problem type?
2. What is the severity?
3. What is the affected unit?
4. What is the root cause?
5. Which patch is needed?
6. Which regression test should be added?
7. Is human approval required?
8. Which changelog note should be created?
```

After this, it becomes clear that feedback is not merely a comment. It is an input to the Ordo-program development process.

---

## Short Summary

The `Feedback & Improvement Loop` exists so that real experience with Ordo is not lost.

It transforms user observations into structured improvement records:

```text
feedback → issue → affected unit → root cause → patch → test → approval → regression → changelog
```

This layer makes Ordo a language not only for execution but also for controlled instruction evolution.

Without a feedback loop, complex playbooks gradually become chaotic.

With a feedback loop, every problem can become a source of controlled improvement.

<!-- REVIEWED: chapter 18; Nebu markers checked -->
