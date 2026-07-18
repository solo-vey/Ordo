# Chapter 21. FREEFORM.COVERAGE

In the previous chapters, we established that Ordo needs `FREEFORM`. Not everything can or should be converted into strict opcodes, tables, and gates. Some knowledge will always remain as explanations, examples, domain nuances, historical notes, or instructions for a person.

But this creates a new problem.

If `FREEFORM` is allowed, we need to understand:

```text
how much important logic remains in FREEFORM;
where exactly it is located;
what it affects;
whether it can be tested;
whether critical rules are hidden there;
what should be formalized later.
```

This is why Ordo needs the `FREEFORM.COVERAGE` construct.

## Why FREEFORM.COVERAGE Is Needed

Without coverage, `FREEFORM` quickly becomes a black box.

At first glance, a playbook may look structured: it has paths, nodes, gates, outputs, and statuses. But some of the real rules may still remain in free text.

For example:

```text
In complex cases, do not create the final package without an additional check.
```

If this is merely a phrase in FREEFORM, the model may follow it once, skip it another time, interpret it differently, or fail to understand that it is a blocking rule.

`FREEFORM.COVERAGE` exists to make such places visible.

It answers:

```text
Which part of the process has already been formalized, and which part still lives in free text?
```

## FREEFORM Is Not an Error

It is important not to treat `FREEFORM` as something bad.

In a good Ordo document, `FREEFORM` may be completely normal and necessary. The problem is not that it exists. The problem is not knowing what role it plays.

There is safe FREEFORM:

```text
explanations for an analyst;
wording examples;
domain context descriptions;
historical reasons for a rule;
term explanations;
style recommendations.
```

And there is dangerous FREEFORM:

```text
hidden gates;
hidden prohibitions;
conditions for transitions between paths;
output creation rules;
process stop conditions;
exceptions that change model behavior.
```

`FREEFORM.COVERAGE` helps distinguish these two cases.

## What Exactly Should Be Covered

Coverage should show more than the amount of text in FREEFORM. Text volume itself is not the main issue.

It is much more important to understand whether FREEFORM affects execution.

For every FREEFORM block, we need to know:

```text
block id;
where it is located;
which path/node/gate/output it is bound to;
what role it performs;
whether it affects model decisions;
whether it contains rules;
whether it contains examples;
whether tests are required for it;
whether improvement records are linked to the block;
whether it should be formalized later.
```

In a simple form:

```yaml
freeform_coverage:
  entries:
    - id: "FF_DOMAIN_CONTEXT_01"
      location: "History Event Domain Pack / Path A1"
      role: "domain_explanation"
      affects_execution: false
      test_required: false
      formalization_needed: false

    - id: "FF_EDGE_CASE_02"
      location: "Package Generation / Final Archive"
      role: "conditional_rule"
      affects_execution: true
      test_required: true
      formalization_needed: true
      suggested_formalization:
        - "convert to GATE.DEF"
        - "add ASSERT.NOT before final archive"
```

## Roles of FREEFORM Blocks

For coverage to be useful, every FREEFORM block should have a role.

Base roles may include:

```text
explanation
example
note
warning
domain_context
style_guidance
edge_case
conditional_rule
human_instruction
migration_note
implementation_hint
```

Not all roles have the same risk.

For example:

```text
example — usually low risk;
explanation — low or medium risk;
warning — medium risk;
edge_case — medium or high risk;
conditional_rule — high risk;
human_instruction — depends on context;
implementation_hint — high risk if it affects output or tests.
```

Coverage should therefore do more than count blocks. It should provide a risk view.

## Risk View

Ordo can use a simple risk classification:

```text
low
medium
high
critical
```

For example:

```yaml
freeform_risk_summary:
  total_entries: 12
  low: 6
  medium: 3
  high: 2
  critical: 1

critical_entries:
  - id: "FF_NO_ARCHIVE_WITHOUT_SELF_CHECK"
    reason: "contains blocking behavior but is not represented as gate"
    action: "formalize_before_release"
```

If a FREEFORM block has `critical` risk, the Ordo program should not be considered ready for production use until a decision is made:

```text
formalize it;
cover it with a test;
or explicitly accept the risk.
```

## FREEFORM.COVERAGE and Tests

FREEFORM that affects behavior should be covered by tests.

For example, if FREEFORM says:

```text
If the user asks to create an archive before approval, the process must stop.
```

This is no longer merely an explanation. It is a behavioral rule.

It needs a test case:

```yaml
test:
  id: "TC_FREEFORM_NO_ARCHIVE_BEFORE_APPROVAL"
  method: human
  trust_class: human_decision

fixture:
  user_message: "create the archive immediately"

expected:
  gate:
    id: "G_PRE_ARCHIVE_APPROVAL"
    status: "blocked"

  output:
    archive_created: false
```

Coverage should show that this FREEFORM block has either already been formalized as a gate or is at least checked by a test.

## FREEFORM.COVERAGE and the Improvement Loop

If a user repeatedly points out a problem originating in a FREEFORM block, that is a strong signal.

For example:

```text
The edge case was interpreted incorrectly again.
```

The improvement record should then refer not only to the run or node but also to the specific FREEFORM block:

```yaml
improvement_record:
  id: "IR-002"
  classification:
    type: "ambiguous_freeform_rule"
    severity: "high"

  affected_unit:
    kind: "freeform"
    id: "FF_EDGE_CASE_02"

  proposed_patch:
    - "split FREEFORM block into explanation and rule"
    - "convert rule part into GATE.DEF"
    - "add regression test"
```

This turns `FREEFORM.COVERAGE` from a report into part of the Ordo-program improvement cycle.

## Formalization Over Time

In the first version of a playbook, some logic may remain in FREEFORM. That is normal.

But Ordo should support gradual formalization.

The cycle may look like this:

```text
FREEFORM explanation
→ feedback reveals a problem
→ debug trace shows the location
→ coverage marks high risk
→ author formalizes the rule
→ gate/assertion/test is added
→ regression suite verifies the change
```

`FREEFORM.COVERAGE` therefore helps evolve an Ordo program without abruptly rewriting the entire document.

## Minimum FREEFORM.COVERAGE Report

For simple Ordo programs, a short report is enough:

```yaml
freeform_coverage_report:
  total_entries: 5
  execution_affecting_entries: 1
  tested_entries: 1
  high_risk_entries: 0
  formalization_required: false
```

Large playbooks need a more detailed report:

```yaml
freeform_coverage_report:
  total_entries: 28
  by_role:
    explanation: 8
    example: 6
    domain_context: 5
    edge_case: 4
    conditional_rule: 3
    warning: 2

  execution_affecting:
    total: 7
    covered_by_tests: 5
    not_covered:
      - "FF_EDGE_CASE_07"
      - "FF_STATUS_WARNING_02"

  formalization_candidates:
    - id: "FF_EDGE_CASE_07"
      suggested_target: "GATE.DEF"
    - id: "FF_STATUS_WARNING_02"
      suggested_target: "STATUS.SEMANTICS"

  release_status: "blocked_until_review"
```

## Typical Mistakes

The first mistake is counting only the amount of FREEFORM.

There may be a large amount of safe FREEFORM and very little dangerous FREEFORM. Or there may be one short FREEFORM block that effectively changes the entire process behavior.

The second mistake is failing to bind FREEFORM to a specific execution location.

If a block is not bound to a path, node, gate, output, or domain rule, it is difficult to test and improve.

The third mistake is leaving a blocking rule in FREEFORM.

Anything that should stop the process must be a gate or assertion.

The fourth mistake is failing to test FREEFORM edge cases.

If FREEFORM describes a complex exception, it needs a test case.

The fifth mistake is failing to move recurring FREEFORM problems into the improvement backlog.

If the same error occurs several times, it is no longer random. It is a signal that the Ordo program should be improved.

## Mini-Exercise

Take any playbook fragment containing free text and answer five questions:

```text
1. Is this an explanation, example, warning, or rule?
2. Does this text affect a model decision?
3. Could an incorrect interpretation of this text break the process?
4. Is there a test for it?
5. Should it be formalized as a gate, assertion, status, or output rule?
```

If the answer to the second or third question is “yes,” this FREEFORM block should be visible in the coverage report.

## Short Summary

`FREEFORM.COVERAGE` exists so that Ordo does not turn back into one large uncontrolled prompt.

FREEFORM preserves human meaning, domain explanations, and complex nuances. But everything that affects execution must be visible, bound, risk-assessed, and, when necessary, covered by tests.

The main idea of this chapter is simple:

```text
FREEFORM is allowed, but it must not be invisible.
```

In a mature Ordo program, every important FREEFORM block should answer three questions:

```text
where is it used;
what does it affect;
how do we verify that it does not break the process.
```

---
