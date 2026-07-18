# Chapter 33. What Remains in FREEFORM

## Why This Is Needed

We have already discussed that Ordo should not try to formalize absolutely everything. Some knowledge needs `FREEFORM`: explanations, examples, warnings, historical notes, and complex domain wording.

But after migrating a large playbook to Ordo, one question always appears:

```text
What exactly remains in FREEFORM?
```

This is not a minor detail. The answer shows the maturity level of an Ordo program.

If FREEFORM contains only material that truly should not be formalized, that is normal.

If gates, required decisions, status rules, or output contracts accidentally remain in FREEFORM, that is a problem. The model may miss them, interpret them incorrectly, or execute them inconsistently.

---

## Simple Explanation

FREEFORM is the area where Ordo allows human text to remain human.

But this area must be transparent.

After migration, we need to examine:

```text
what was converted into structured Ordo;
what remains in FREEFORM;
why it remains there;
whether this is safe;
whether tests are needed;
whether some of this text should gradually be formalized.
```

Otherwise, FREEFORM may become a “dark room” where critical rules are hidden.

---

## What Is Normal to Leave in FREEFORM

It is normal to leave the following in FREEFORM:

```text
- explanations for people;
- examples;
- long domain descriptions;
- decision history;
- edge cases that are not yet stable;
- analytical comments;
- stylistic recommendations;
- temporary notes;
- text templates, if they are not execution rules.
```

For example:

```yaml
freeform:
  id: "FF_DOMAIN_CONTEXT"
  purpose: "domain context explanation"
  content: |
    In this type of historical event, it is important to distinguish a change
    to the primary company from a change to a related entity. The analyst must
    carefully verify the source of the change.
```

This is normal FREEFORM if the path-selection rules themselves have already been formalized separately.

---

## What Must Not Be Hidden in FREEFORM

FREEFORM must not contain anything that affects execution as a mandatory rule.

For example, this is bad:

```yaml
freeform:
  content: |
    A self-check must always be performed before creating the archive.
```

If the rule is mandatory, it must be a gate:

```yaml
gate:
  id: "G_PACKAGE_SELF_CHECK"
  method: mechanical
  trust_class: deterministic
  type: "blocking"
  before:
    - "handoff"
    - "archive_delivery"
```

Likewise, the following must not be hidden in FREEFORM:

```text
- blocking gates;
- required fields;
- status semantics;
- output contracts;
- path-selection rules;
- approval requirements;
- negative assertions;
- regression requirements;
- library conflict rules;
- no-op conditions.
```

---

## FREEFORM After Playbook Migration

When an old Markdown playbook is migrated to Ordo, part of the text becomes structured IR and part remains FREEFORM.

For example:

```text
Before, in Markdown:
"If the event concerns a related entity, the relation must be clarified through the Identification Center."

After migration:
- path rule → structured;
- required question → NODE.DEF;
- state field → STATE.SCHEMA;
- explanation of the Identification Center → FREEFORM.
```

So FREEFORM does not mean “unimportant.” It means:

```text
this knowledge is needed, but it is not an independent execution instruction.
```

---

## FREEFORM Ledger

A large Ordo program needs a FREEFORM ledger.

```yaml
freeform_ledger:
  - id: "FF_HISTORY_EVENT_CONTEXT"
    source_section: "old_playbook/domain_notes"
    reason: "domain explanation, not executable rule"
    bound_to:
      - "DOMAIN_PACK.history_event"
      - "PATH.A2"
    risk: "low"
    tests_required: false

  - id: "FF_EDGE_CASES_EXTERNAL_EVENTS"
    source_section: "old_playbook/external_history_event_notes"
    reason: "edge cases not fully formalized yet"
    bound_to:
      - "PATH.A4"
    risk: "medium"
    tests_required: true
```

The ledger is needed so that residual human text does not escape control.

---

## FREEFORM Coverage

FREEFORM also needs coverage.

Coverage should answer:

```text
- how many FREEFORM blocks exist in the program;
- which are bound to paths/nodes/gates;
- which have tests;
- which have known risks;
- which should be formalized later;
- which have already caused user feedback or problems.
```

Example:

```yaml
freeform_coverage:
  total_blocks: 5
  bound_blocks: 5
  tested_blocks: 3
  untested_blocks:
    - "FF_EDGE_CASES_EXTERNAL_EVENTS"
    - "FF_LEGACY_STATUS_NOTES"

  high_risk_blocks:
    - "FF_LEGACY_STATUS_NOTES"

  recommended_actions:
    - "formalize status notes into STATUS.SEMANTICS"
    - "add regression tests for external event edge cases"
```

---

## FREEFORM and the Debug Layer

In debug mode, Ordo must show when a decision relied on FREEFORM.

For example:

```yaml
trace_source: "model_self_report"
knowledge_trace:
  - source_type: "freeform"
    id: "FF_EDGE_CASES_EXTERNAL_EVENTS"
    used_for: "path disambiguation"
    risk: "medium"
```

This matters because if an incorrect decision was based on FREEFORM, we can see exactly which block needs improvement.

Without this, the model may say:

```text
that is how I understood the instruction
```

Ordo should say more precisely:

```text
the decision used FREEFORM block FF_EDGE_CASES_EXTERNAL_EVENTS, which has medium risk and no regression test.
```

---

## FREEFORM and the Improvement Loop

If a user identifies a problem connected to FREEFORM, Ordo should create an improvement record.

```yaml
improvement_record:
  type: "freeform_caused_ambiguity"
  affected_unit:
    kind: "freeform"
    id: "FF_LEGACY_STATUS_NOTES"
  problem:
    description: "status rule was interpreted inconsistently"
  proposed_patch:
    - "extract status meanings into STATUS.SEMANTICS"
    - "leave only explanation in FREEFORM"
  suggested_tests:
    - "TC_STATUS_READY_FOR_FIRST_RUN"
```

This makes FREEFORM not merely “residual text,” but a controlled part of the language.

---

## How to Decide What to Formalize Next

After migration, there is no need to formalize everything immediately. But criteria are needed.

A FREEFORM block should be formalized further if it:

```text
- is frequently used for decisions;
- affects gates;
- affects status;
- frequently causes errors;
- has multiple interpretations;
- is needed for regression scenarios;
- is repeated across many Domain Packs;
- could become a reusable library.
```

A block may remain in FREEFORM if it:

```text
- only explains context;
- does not change the path;
- does not block output;
- does not define required fields;
- does not conflict with structured rules;
- is easy for a person to verify.
```

---

## Typical Mistakes

### Mistake 1. Treating FREEFORM as a Dumping Ground

FREEFORM is not a place for everything that someone is too lazy to formalize.

### Mistake 2. Hiding Gates in Text

If a rule blocks an action, it must be a gate.

### Mistake 3. Not Maintaining a FREEFORM Ledger

Without a ledger, it is impossible to understand what remains unformalized.

### Mistake 4. Not Testing Risky FREEFORM

If FREEFORM affects decisions, tests are needed.

### Mistake 5. Not Revisiting FREEFORM After Feedback

If a user repeatedly identifies a problem, the FREEFORM must be improved or formalized.

---

## Mini-Exercise

Take any long instruction document.

Write down five fragments that are difficult to formalize.

For each one, determine:

```text
1. Is this an explanation or a rule?
2. Does it affect the path?
3. Does it block output?
4. Should it be a gate?
5. Does it need a test?
6. Can it remain in FREEFORM?
```

---

## Short Summary

After migrating a playbook to Ordo, it is important not only to show what was formalized. It is equally important to show what remains in FREEFORM.

FREEFORM must be controlled, bound to specific parts of the program, covered by tests where necessary, and visible to the debug and improvement loops.

Good FREEFORM is not chaos. It is an honestly marked area of human knowledge that has not yet become fully formal, but is already governed by Ordo rules.
