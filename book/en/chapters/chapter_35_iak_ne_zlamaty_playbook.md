# Chapter 35. How Not to Break a Playbook

## Why This Is Needed

A large playbook is not merely a long instruction. It is a system of rules, decisions, stops, checks, examples, exceptions, and expected results. As such a system grows, even a good change can easily break it.

Most often, a playbook does not break because someone made an obvious mistake. More often, everything looks harmless:

```text
- a new clarification was added;
- a block was moved higher;
- repetition was removed;
- two rules were merged;
- part of the text was moved into FREEFORM;
- gate wording was changed;
- a new path was added;
- one scenario was fixed without checking the others.
```

Afterward, the model suddenly starts asking questions in the wrong order, skipping approval, generating the final artifact too early, or confusing an example with a rule.

Ordo exists precisely so that such changes are not made blindly.

## Simple Explanation

Breaking a playbook means violating the expected behavior of the process.

You do not have to break the entire document. Breaking one important property is enough:

```text
- the model followed the wrong path;
- a gate stopped being blocking;
- a node started asking unnecessary questions;
- state began updating earlier than required;
- output is created without confirmation;
- FREEFORM started behaving like a hidden rule;
- a library overwrote a local rule;
- a test passes formally, but the real artifact is wrong.
```

In ordinary instructions, such problems are difficult to see. In Ordo, every important part of a playbook should be connected to a path, node, gate, state, output, trace, or test.

The main rule is therefore simple:

```text
Do not change a playbook as text. Change it as an execution system.
```

## What Counts as a Dangerous Change

Not all changes carry the same risk.

Low risk:

```text
- fixing a textual error;
- clarifying an explanation without changing rules;
- adding an example explicitly marked as an example;
- improving a section title without changing execution flow.
```

Medium risk:

```text
- adding a new question;
- changing node order;
- clarifying a condition;
- changing an output template;
- moving part of the logic into a library;
- changing a FREEFORM block.
```

High risk:

```text
- changing path selection;
- changing gate semantics;
- changing status semantics;
- changing a blocking rule;
- changing approval flow;
- changing ASSERT.NOT;
- changing compiler mapping;
- changing a Domain Pack rule;
- changing a reusable library used by several playbooks.
```

For Ordo, this means: the closer a change is to execution behavior, the stronger the required validation.

## Ordo Construct

Safe playbook changes require a dedicated change flow in Ordo.

Minimum flow:

```text
CHANGE.PROPOSE
→ IMPACT.ANALYZE
→ AFFECTED.UNIT
→ TEST.SELECT
→ REGRESSION.RUN
→ TRACE.COMPARE
→ HUMAN.APPROVE
→ VERSION.NOTE
```

This means a change should not simply be “inserted into the text.” Its impact must be described.

Example:

```yaml
change:
  id: "CH-001"
  type: "gate_semantics_update"
  summary: "Make package self-check gate blocking"

affected_units:
  - kind: "gate"
    id: "G_PACKAGE_SELF_CHECK"
  - kind: "assertion"
    id: "ASSERT_NO_ARCHIVE_BEFORE_SELF_CHECK"
  - kind: "test"
    id: "TC_NO_ARCHIVE_WITHOUT_SELF_CHECK"

risk:
  level: "high"
  reason: "Changes final package generation behavior"

required_checks:
  - "run_regression_suite"
  - "compare_debug_trace"
  - "validate_rendered_artifacts"
  - "human_approval"
```

## Principle 1. Do Not Change a Rule Without a Test

Every rule change must either use an existing test or create a new one.

Bad:

```text
Added a rule: a self-check is mandatory before creating the archive.
```

Better:

```text
Added the rule + added a test:
TC_NO_ARCHIVE_WITHOUT_SELF_CHECK
```

In Ordo, this should be an almost automatic requirement:

```text
RULE.CHANGE requires TEST.DEF or TEST.UPDATE
```

Otherwise, a change may look correct but remain unprotected against regression.

## Principle 2. Do Not Change a Gate Without Status Semantics

A gate is a control point. But a gate only makes sense when the meaning of its statuses is clear.

For example:

```text
passed
failed
blocked
pending
not_applicable
```

If a gate changes without checking status semantics, a dangerous situation may arise: the model sees the gate but does not understand whether it must stop.

The rule is therefore:

```text
GATE.CHANGE requires STATUS.SEMANTICS.CHECK
```

This is especially important for blocking gates.

## Principle 3. Do Not Hide Behavior in FREEFORM

FREEFORM is useful when part of an instruction is not ready for formalization. But FREEFORM must not become a place for hidden gates, path selection, or approval rules.

Bad:

```text
FREEFORM says: “usually the package should be checked before the archive is created.”
```

Better:

```text
Gate:
  id: G_PACKAGE_SELF_CHECK
  blocking: true

FREEFORM:
  explains how the analyst usually checks the package.
```

FREEFORM may explain a rule, but it must not replace the rule itself.

## Principle 4. Do Not Use Implicit Overrides

When a playbook uses libraries, Profiles, or Domain Packs, behavior can easily be overwritten by accident.

For example, a library has a gate:

```text
G_CONTRACT_CONFIRMED
```

And the local playbook adds a gate with the same name but different logic.

Ordo must not silently accept this.

Correct:

```yaml
override:
  target: "contract_first.G_CONTRACT_CONFIRMED"
  allow: true
  reason: "Domain pack requires additional source row confirmation"
  approved_by: "human"
```

Without an explicit override, the change must be blocked or marked as a conflict.

## Principle 5. Validate Not Only the Template, but the Rendered Artifact

A common mistake is checking the template but not the finished document.

For example, the template may contain the correct block, but the final artifact may omit it because of an error in the render step.

Ordo therefore needs the rule:

```text
Artifact is valid only after rendered artifact validation.
```

It is not enough to say:

```text
the template has a self-check section
```

You must verify:

```text
the finished file has the self-check section in the correct place and with the correct content
```

## Principle 6. Compare the Trace Before and After a Change

For complex playbooks, knowing that tests passed is not enough. You also need to see whether the execution path changed.

Before the change:

```text
input → path A1 → node collect_alias → gate contract_confirmed → output draft
```

After the change:

```text
input → path A1 → node collect_source_field → node collect_alias → gate contract_confirmed → output draft
```

This may be the correct change. But it must be visible.

Ordo should therefore support:

```text
TRACE.COMPARE
```

Trace comparison shows:

```text
- which paths changed;
- which nodes were added or removed;
- which gates changed status;
- which state fields changed;
- which outputs changed structure;
- which warnings appeared or disappeared.
```

## Small Example

Imagine that a historical-events playbook sometimes creates the final archive without self-validation.

Bad fix:

```text
Add to the text: “Do not forget to perform a check before creating the archive.”
```

This wording may be lost again.

Better Ordo fix:

```yaml
assert_not:
  id: "ASSERT_NO_ARCHIVE_BEFORE_VALIDATION"
  method: mechanical
  trust_class: deterministic
  condition: "final_archive_created == true and validation_passed != true"
  severity: "blocking"

expected_behavior:
  if_assertion_triggered:
    action: "stop"
    message: "Cannot create final archive before validation is passed."

test:
  id: "TC_NO_ARCHIVE_BEFORE_VALIDATION"
  fixture:
    user_message: "create the archive immediately"
  expected:
    output:
      final_archive_created: false
    gate:
      id: "G_VALIDATION_BEFORE_ARCHIVE"
      status: "blocked"
```

Now this is not merely advice. It is part of the execution contract.

## Typical Mistakes

The first mistake is editing a playbook as an article.

If a playbook is treated as text, the author thinks about elegant wording. If it is treated as an Ordo program, the author thinks about model behavior.

The second mistake is adding rules without tests.

A rule without a test can easily be broken two days later, even if it seems obvious today.

The third mistake is failing to distinguish an example from a rule.

Examples help the model, but if they are not clearly marked, the model may begin executing an example as a mandatory scenario.

The fourth mistake is assuming that a shorter document is automatically better.

Compression may destroy important gates, warnings, or domain-specific exceptions.

The fifth mistake is failing to check old scenarios after a new improvement.

Many changes look correct locally but break a neighboring path.

## Mini-Exercise

Take any complex playbook or instruction and choose one change you want to make.

Before making the change, write down:

```text
1. Which behavior should this change improve?
2. Which path or node does it affect?
3. Which gate may change status?
4. Which state field may change?
5. Which output may change?
6. Which test should be added?
7. Which regression test should be run?
8. Is human approval required?
```

If these questions do not have answers, the change is not ready.

## Short Summary

A playbook breaks when it is changed as text rather than as an execution system.

To avoid breaking a playbook, Ordo requires:

```text
- describe the impact of the change;
- bind the change to affected units;
- do not change a rule without a test;
- do not change a gate without status semantics;
- do not hide behavior in FREEFORM;
- do not use implicit overrides;
- validate the rendered artifact;
- compare traces before and after the change;
- run the regression suite;
- record a version note.
```

Without this, any improvement can accidentally become a new defect.
