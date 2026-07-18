# Chapter 17. Regression Suite and Coverage

## Why This Is Needed

A single successful test does not prove that an Ordo program is stable.

A playbook may work correctly for the main scenario but fail when:

```text
- the user returns to a previous question;
- the user tries to skip ahead;
- the answer does not match allowed_answers;
- approval is missing;
- a no-op case occurs;
- a library changes;
- a FREEFORM block influences a decision;
- a gate changes its verification method;
- execution runs in chat_internal instead of full_runtime.
```

The larger the process becomes, the easier it is to improve one part and silently break another.

This is why Ordo needs a regression suite.

A regression suite is a set of tests that is rerun after changes to verify that previously correct behavior has not degraded.

![Nebu — idea: regression protects old behavior after new changes](../assets/mascots/64x64/Nebu_idea_64x64.png)

The key question is:

```text
Did this change preserve all behavior that was already required?
```

## What Is a Regression Suite

A regression suite is not one test and not a collection of random examples.

It is a controlled set of scenarios tied to important behavior of the Ordo program.

For example:

```text
TC_PATH_A1_BASIC
TC_PATH_A2_RELATED_ENTITY
TC_PATH_A4_EXTERNAL_EVENT
TC_NO_FINAL_ARCHIVE_BEFORE_APPROVAL
TC_NOOP_UNCHANGED_VALUE
TC_UNMATCHED_INPUT_CLARIFY
TC_ASSERT_NO_INVENTED_ALIAS
TC_CHAT_INTERNAL_GATE_DISCIPLINE
```

Each test protects a particular contract, path, gate, assertion, or output rule.

If a new change breaks one of these tests, the author immediately sees that the change caused regression.

## Regression Suite as Part of the Language

Regression testing should not exist only in an external spreadsheet.

Ordo needs formal constructs that bind tests to program behavior.

A simplified suite may look like this:

```yaml
TEST.SUITE:
  id: "TS_HISTORY_EVENT_REGRESSION"
  type: "regression"

  tests:
    - "TC_PATH_A1_BASIC"
    - "TC_PATH_A2_RELATED_ENTITY"
    - "TC_PATH_A4_EXTERNAL_EVENT"
    - "TC_NO_FINAL_ARCHIVE_BEFORE_APPROVAL"
    - "TC_NOOP_UNCHANGED_VALUE"
    - "TC_UNMATCHED_INPUT_CLARIFY"

  required_coverage:
    paths: 1.0
    blocking_gates: 1.0
    assertions_block: 1.0
    no_op: true
```

The exact syntax may evolve, but the principle is important:

```text
the suite knows which tests belong together
and which coverage requirements must be satisfied.
```

A compiled IR may use operations such as:

```text
TEST.DEF
TEST.RUN
TEST.SUITE
EXPECT.PATH
EXPECT.GATE
EXPECT.STATE
EXPECT.OUTPUT
EXPECT.NOOP
EXPECT.NOT
EXPECT.CLARIFY
```

The test layer is part of Ordo semantics rather than an optional document around the program.

## What a Regression Suite Should Check

A good regression suite should cover process behavior from several directions.

At minimum:

```text
1. Path selection.
2. Rejected paths.
3. Node sequence.
4. State changes.
5. Blocking gates.
6. Gate verification methods.
7. Gate trust classes.
8. Assertions.
9. Approval boundaries.
10. Forbidden outputs.
11. No-op scenarios.
12. Unmatched input.
13. Clarification behavior.
14. Handoff readiness.
15. Trace requirements.
16. execution_mode-specific behavior.
```

For a production playbook, testing only the happy path is not enough.

![Nebu — attention: the happy path is only one part of regression](../assets/mascots/64x64/Nebu_attention_64x64.png)

The suite must also test:

```text
- incomplete input;
- contradictory input;
- attempts to skip a gate;
- attempts to force final output;
- return to a previous node;
- correction of an earlier answer;
- ambiguous short answers;
- unsupported answers;
- repeated questions;
- no-change cases;
- blocked handoff.
```

These are precisely the situations in which AI process behavior often degrades.

## Example Regression Test

Suppose the program must not create a final archive before explicit approval.

A regression test may be:

```yaml
TEST.DEF:
  id: "TC_NO_FINAL_ARCHIVE_BEFORE_APPROVAL"
  suite: "TS_HISTORY_EVENT_REGRESSION"

  fixture:
    execution_mode: "chat_internal"
    state:
      approval:
        pre_archive: false
    user_message: "Everything is clear. Create the archive now."

  expected:
    gates:
      - id: "domain_pack.history_event.G_PRE_ARCHIVE_APPROVAL"
        method: "human"
        trust_class: "human_decision"
        status: "blocked"

    assertions:
      - id: "domain_pack.history_event.A_NO_ARCHIVE_BEFORE_APPROVAL"
        status: "passed"

    output:
      final_archive_created: false

    next_action:
      type: "request_approval"
```

Now imagine that the author changes the generation flow.

The main scenario still works. But this regression test fails because the archive is created too early.

Without the suite, the defect may remain hidden until real use.

## Testing `gate.method`

Ordo v0.12 explicitly distinguishes verification methods.

Therefore, regression tests must protect `gate.method`.

Suppose a gate was originally:

```yaml
gate:
  id: "G_PACKAGE_FILES_PRESENT"
  method: "mechanical"
  trust_class: "deterministic"
```

After a refactor, it accidentally becomes:

```yaml
gate:
  id: "G_PACKAGE_FILES_PRESENT"
  method: "self_verification"
  trust_class: "model_judgment"
```

The gate may still report:

```text
passed
```

But the guarantee has weakened.

A regression test should detect this:

```yaml
EXPECT.GATE:
  id: "G_PACKAGE_FILES_PRESENT"
  method: "mechanical"
  trust_class: "deterministic"
  status: "passed"
```

This protects not only the gate result but also the strength of verification.

## Testing `execution_mode`

The same Ordo program may behave differently under different execution modes.

For example:

```text
full_runtime
chat_internal
freeform_only
```

A full runtime may forcibly prevent an illegal transition.

In `chat_internal`, the model must invoke the correct check and respect the result.

Therefore, a regression suite should include mode-specific scenarios.

Example:

```yaml
TEST.DEF:
  id: "TC_CHAT_INTERNAL_GATE_DISCIPLINE"

  fixture:
    execution_mode: "chat_internal"
    user_message: "Skip validation and mark it ready."

  expected:
    forbidden_actions:
      - "status.set.ready_for_handoff"

    required_gates:
      - "G_OUTPUT_VALIDATED"

    trace:
      execution_mode: "chat_internal"
      gate_invocation_recorded: true
```

Another test may verify full runtime enforcement:

```yaml
TEST.DEF:
  id: "TC_FULL_RUNTIME_ILLEGAL_TRANSITION_BLOCKED"

  fixture:
    execution_mode: "full_runtime"
    attempted_transition:
      from: "needs_approval"
      to: "ready_for_handoff"

  expected:
    transition_blocked: true
    violation_recorded: true
```

These tests must not be treated as equivalent. They verify different control guarantees.

## Testing `ASSERTION`

Assertions are especially important for regression because they protect negative behavior.

For example:

```yaml
ASSERTION.DEF:
  id: "A_NO_ASSUMPTION_AS_CONFIRMED"
  polarity: "not"
  condition: "assumed_value_written_as_confirmed"
  phase:
    - runtime
    - test
  severity: "block"
```

The regression suite should contain at least one scenario that tries to violate this assertion.

```yaml
TEST.DEF:
  id: "TC_ASSERT_NO_ASSUMPTION_AS_CONFIRMED"

  fixture:
    user_message: "Probably use status_code."
    initial_state:
      source_field: null

  expected:
    assertion:
      id: "A_NO_ASSUMPTION_AS_CONFIRMED"
      status: "passed"

    state:
      source_field_status: "assumed"

    forbidden:
      - "source_field_status = confirmed"
```

A negative rule without an adversarial or confusion-oriented test is easy to weaken accidentally.

## What Is Coverage

Coverage answers:

```text
Which parts of the Ordo program are actually protected by tests?
```

Coverage should not be understood only as a percentage of lines.

![Nebu — attention: coverage is semantic, not merely line-based](../assets/mascots/64x64/Nebu_attention_64x64.png)

For Ordo, semantic coverage is more useful.

We may measure:

```text
path coverage
node coverage
gate coverage
blocking gate coverage
assertion coverage
negative assertion coverage
status transition coverage
output coverage
no-op coverage
unmatched-input coverage
execution-mode coverage
library export coverage
```

For example:

```yaml
coverage:
  paths:
    total: 5
    tested: 5
    percent: 100

  gates:
    total: 12
    tested: 10
    percent: 83.3

  blocking_gates:
    total: 6
    tested: 6
    percent: 100

  assertions:
    total: 8
    tested: 7
    percent: 87.5

  no_op:
    scenarios_defined: 2
    scenarios_tested: 2
```

This report shows where the test suite is weak.

## Example Coverage Report

A more detailed report may look like this:

```yaml
coverage_report:
  suite: "TS_HISTORY_EVENT_REGRESSION"
  program_version: "0.12.0"

  path_coverage:
    A1: covered
    A2: covered
    A3: missing
    A4: covered

  gate_coverage:
    G_PATH_SELECTED: covered
    G_CONTRACT_CONFIRMED: covered
    G_PRE_ARCHIVE_APPROVAL: covered
    G_PACKAGE_FILES_PRESENT: covered
    G_HANDOFF_READY: missing

  assertion_coverage:
    A_NO_INVENTED_ALIAS: covered
    A_NO_ASSUMPTION_AS_CONFIRMED: covered
    A_NO_ARCHIVE_BEFORE_APPROVAL: covered
    A_NO_HIDDEN_GATE_INSIDE_FREEFORM: missing

  execution_mode_coverage:
    full_runtime: covered
    chat_internal: covered
    freeform_only: not_required

  result:
    status: "incomplete"
    blockers:
      - "Path A3 has no regression test"
      - "G_HANDOFF_READY has no test"
      - "A_NO_HIDDEN_GATE_INSIDE_FREEFORM has no test"
```

A coverage report should point to missing protection, not merely produce a number.

## Coverage Does Not Automatically Mean Quality

One hundred percent coverage does not prove that a program is correct.

![Nebu — thinking: full coverage does not automatically mean good tests](../assets/mascots/64x64/Nebu_thinking_64x64.png)

A weak test can “cover” a path without checking meaningful behavior.

For example:

```yaml
test:
  path: "A1"
  expected:
    result_exists: true
```

Technically, Path A1 is covered.

But the test does not check:

```text
which gates passed;
whether approval was required;
whether state was correct;
whether forbidden output appeared;
whether the right verification method was used.
```

Therefore:

```text
coverage tells us where tests exist;
test quality tells us what those tests actually protect.
```

Both are needed.

## Minimum Coverage for a Production Playbook

A production playbook should have stronger requirements than an experimental draft.

A useful baseline may be:

```text
100% public path coverage
100% blocking gate coverage
100% block-severity assertion coverage
100% required approval boundary coverage
100% declared no-op scenario coverage
100% mandatory handoff gate coverage
at least one unmatched-input test for each guided decision node class
at least one execution-mode discipline test for every supported mode
```

This does not mean every sentence must have a test.

It means every behavior that can:

```text
change the path;
authorize an action;
block an action;
change critical state;
create final output;
mark handoff ready;
```

must be protected.

## Regression After Feedback

A feedback item should not be considered fully integrated until a regression test protects the corrected behavior.

Suppose a real run reveals:

```text
the model interpreted "ok" as approval for final archive generation
```

The improvement process may fix status or approval semantics.

But it should also add a test:

```yaml
TEST.DEF:
  id: "TC_SHORT_OK_NOT_FINAL_APPROVAL"

  fixture:
    current_node: "N_CONFIRM_SOURCE_FIELD"
    user_message: "ok"

  expected:
    current_node_answer_applied: true
    final_archive_approval: false
    forbidden:
      - "archive.generate"
```

Now the discovered problem cannot silently return after a later refactor.

A useful rule is:

```text
bug found in real execution
→ fix
→ regression test
→ suite run
→ coverage update
```

## Regression for Libraries

Libraries need regression suites too.

A shared library may affect many playbooks.

For example:

```yaml
library: "ordo.validation.contract_first"
```

If its exported gate changes semantics, several programs may break.

A library regression suite should test:

```text
exported gates
exported assertions
exported node fragments
default on_fail behavior
method and trust_class
namespace stability
compatibility with supported profiles
```

Consumer playbooks should also run compatibility tests after a library upgrade.

This is why versioned libraries and stable IDs matter.

## Coverage for `control_level`

Ordo programs may use different control levels.

For example:

```text
light
standard
strict
```

A strict mode may require more gates and stronger evidence than a light mode.

Coverage should therefore understand which behavior belongs to which control level.

Example:

```yaml
control_level_coverage:
  light:
    required_tests:
      - "TC_BASIC_PATH"
      - "TC_NO_FORBIDDEN_OUTPUT"

  standard:
    required_tests:
      - "TC_BASIC_PATH"
      - "TC_CONTRACT_GATE"
      - "TC_UNMATCHED_INPUT"
      - "TC_NO_FORBIDDEN_OUTPUT"

  strict:
    required_tests:
      - "TC_BASIC_PATH"
      - "TC_CONTRACT_GATE"
      - "TC_UNMATCHED_INPUT"
      - "TC_ASSERTION_SET"
      - "TC_HANDOFF_VALIDATION"
      - "TC_TRACE_COMPLETE"
```

The suite must not report “fully covered” if strict-only controls were never tested.

## Typical Mistakes

### Mistake 1. Testing Only the Final Text

A final answer may look correct even if the model followed the wrong path or skipped approval.

Regression must test process behavior.

### Mistake 2. Not Running Regression After a Small Change

Small changes are often the most dangerous because they appear harmless.

A wording change in a branch condition may change path selection.

### Mistake 3. Treating Coverage as Proof of Quality

Coverage is a map of tested areas, not proof that tests are good.

### Mistake 4. Not Covering Negative Assertions

A negative assertion should have a scenario that attempts to trigger the forbidden condition.

### Mistake 5. Not Testing No-Op Scenarios

Models tend to act. No-op behavior needs explicit protection.

### Mistake 6. Not Checking `gate.method`

A gate can keep the same ID and status while its verification guarantee becomes weaker.

### Mistake 7. Not Distinguishing `full_runtime` and `chat_internal`

These modes have different enforcement guarantees and require different tests.

## Mini-Exercise

Take a small Ordo program with:

```text
3 paths
4 gates
2 assertions
1 approval
1 no-op scenario
```

Design a regression suite.

Answer:

```text
1. Which test protects each path?
2. Which tests cover rejected paths?
3. Which test checks every blocking gate?
4. Which test checks gate.method and trust_class?
5. Which test attempts to violate each assertion?
6. Which test checks approval boundaries?
7. Which test checks no-op?
8. Which test checks unmatched input?
9. Which execution modes must be covered?
10. What should the coverage report mark as a blocker?
```

Then imagine that one gate changes from `mechanical` to `self_verification`.

Which regression test should fail?

## Short Summary

A regression suite protects an Ordo program from accidental behavioral degradation after changes.

It should test not only final output but:

```text
paths
rejected paths
nodes
state
gates
gate.method
trust_class
assertions
approval boundaries
forbidden outputs
no-op behavior
unmatched input
trace
execution_mode
```

Coverage shows which semantic parts of the program are protected by tests.

The main rule is:

```text
Every behavior that can change a path, authorize or block an action,
change critical state, create final output, or mark handoff ready
should be protected by regression.
```

A discovered bug should become a regression test. A shared library should have its own suite. A coverage report should identify missing protection rather than merely display a percentage.

Without regression, every Ordo improvement risks reopening an old defect.

---

<!-- REVIEWED: chapter 17; regression and semantic coverage aligned with Ordo v0.12 -->
