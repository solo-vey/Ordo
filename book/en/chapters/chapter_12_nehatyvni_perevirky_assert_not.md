# Chapter 12. Negative Checks: ASSERT.NOT → ASSERTION

## Why This Is Needed

In ordinary instructions, we often tell a model what it must do:

- create a document;
- ask a question;
- check the structure;
- form a response;
- prepare an archive;
- provide a short summary.

But in real processes, it is equally important to say what the model **must not** do.

For example:

- do not invent missing data;
- do not move to the next step without confirmation;
- do not create the final package before checks pass;
- do not treat an example as a rule;
- do not replace a business decision with a technical guess;
- do not include extra files in the package;
- do not hide uncertainty in the final result.

In prompts, such prohibitions are often lost. A model may read them, agree with them, and still perform an action that is formally forbidden. That is why negative checks in Ordo must be more than textual warnings: they must be separate controlled rules.

![Nebu — idea: ASSERTION protects against forbidden actions](../assets/mascots/64x64/Nebu_idea_64x64.png)

Early Ordo versions used this construct:

```text
ASSERT.NOT
```

Starting with Ordo v0.12, the more precise formulation is:

```text
ASSERTION is the canonical primitive.
ASSERT.NOT is shorthand for ASSERTION with polarity: not.
```

This is an important change. `ASSERT.NOT` is no longer a separate parallel mechanism beside gates and tests. It is one projection of the unified `ASSERTION` rule, which can expand into a runtime check, a test expectation, and a debug violation record.

## Simple Explanation

`ASSERTION` is a formal statement about what must be true or what must not happen in the process.

It has polarity:

```text
must — a required state must hold;
not  — a forbidden state must not occur.
```

Therefore, `ASSERT.NOT` can be understood as an assertion in the opposite direction:

```text
Are we certain that the forbidden thing did not happen?
```

For example:

```text
Gate:
all mandatory sections are present.

ASSERT.NOT:
the final package contains no extra files.
```

Or:

```text
Gate:
the user confirmed the alias.

ASSERT.NOT:
the model did not invent the alias itself.
```

This distinction is very important because a positive check does not always catch a violation.

![Nebu — attention: a positive check does not catch extra behavior](../assets/mascots/64x64/Nebu_attention_64x64.png)

A document may contain all required sections and still contain extra, dangerous, or contradictory blocks. An ordinary gate may say “the structure exists,” while an assertion with `polarity: not` must say “nothing forbidden is present.”

## Why Ordo v0.12 Introduces ASSERTION

Before v0.12, three similar constructs could easily appear in the language:

```text
ASSERT.NOT — a runtime prohibition;
negative gate — a gate checking that a problem is absent;
EXPECT.NOT — a test expectation that a forbidden state does not appear.
```

All three express the same idea: **a certain state or action must not occur**. If they remain separate, the author must manually synchronize the rule across execution, tests, and debug reporting.

For example, an author may add:

```text
ASSERT.NOT final_output_before_validation
```

but forget to add the corresponding `EXPECT.NOT` to the regression suite. The rule then exists in the playbook but is not protected by a test.

Therefore, Ordo v0.12 makes one primitive canonical:

```text
ASSERTION
```

`ASSERT.NOT`, `EXPECT.NOT`, and a negative gate become projections of it.

## Ordo Construct

In Source form, an assertion may look like this:

```yaml
assertions:
  - id: "A_NO_INVENTED_ALIAS"
    polarity: "not"
    condition: "alias_created_without_user_confirmation"
    phase: ["runtime", "test"]
    method: "self_verification"
    severity: "block"
    on_fail: "STOP"
    message: "Alias cannot be invented by the model without user confirmation."
```

This means:

```text
If the alias was created without explicit user confirmation,
the process must stop, and the test suite must contain an expectation
that such a state is not allowed.
```

In compiled IR, it may expand into several representations.

Runtime representation:

```json
{
  "op": "ASSERT.NOT",
  "id": "domain_pack.history_event.A_NO_INVENTED_ALIAS",
  "source_assertion": "domain_pack.history_event.A_NO_INVENTED_ALIAS",
  "condition": "alias_created_without_user_confirmation",
  "method": "self_verification",
  "severity": "block",
  "on_fail": "STOP"
}
```

Test representation:

```json
{
  "op": "EXPECT.NOT",
  "id": "domain_pack.history_event.TE_NO_INVENTED_ALIAS",
  "source_assertion": "domain_pack.history_event.A_NO_INVENTED_ALIAS",
  "condition": "alias_created_without_user_confirmation"
}
```

Debug representation:

```json
{
  "op": "VIOLATION.RECORD",
  "source_assertion": "domain_pack.history_event.A_NO_INVENTED_ALIAS",
  "status": "not_triggered",
  "method": "self_verification"
}
```

Importantly, `ASSERT.NOT` does not merely warn. If `severity: block`, it is a hard stop.

## Method for an Assertion

Ordo v0.12 adds `method` not only to gates but also to assertions when an assertion is checked during execution.

For example:

```yaml
assertions:
  - id: "A_NO_EXTRA_FILES"
    polarity: "not"
    condition: "package_contains_unapproved_files"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"
```

Here `method: mechanical` is appropriate because a runner or script can deterministically compare the actual file list with the allowed list.

Another example:

```yaml
assertions:
  - id: "A_NO_UNCONFIRMED_BUSINESS_DECISION"
    polarity: "not"
    condition: "final_output_contains_business_decision_without_user_confirmation"
    phase: ["runtime", "test"]
    method: "self_verification"
    severity: "block"
```

This is a semantic judgment. A model critic step may check it using an evidence protocol, but we must not pretend that such a check is as reliable as counting files.

## Example Without Ordo

Imagine this prompt:

```text
Prepare an analytical package. Make sure all files are present.
Do not add extra files.
```

The model may create a package containing every required file and also add:

```text
debug_notes.md
draft_old.md
extra_payload.json
```

Then it may respond:

```text
The package is ready. All files are present.
```

Formally, it checked the positive condition. But the prohibition was violated.

## Example with Ordo v0.12

In Ordo, this is better described as:

```yaml
output:
  required_files:
    - "README.md"
    - "SUMMARY.json"
    - "VALIDATION_REPORT.json"

allowed_files:
  - "README.md"
  - "SUMMARY.json"
  - "VALIDATION_REPORT.json"

gates:
  - id: "G_REQUIRED_FILES_PRESENT"
    method: "mechanical"
    trust_class: "deterministic"
    check: "all_required_files_exist"
    on_fail: "STOP"

assertions:
  - id: "A_NO_EXTRA_FILES"
    polarity: "not"
    condition: "package_contains_files_outside_allowed_files"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"
    on_fail: "STOP"
```

The final response is then possible only if:

```text
1. all required files exist;
2. there are no extra files;
3. both checks have an explicit method;
4. the test suite automatically receives EXPECT.NOT for the forbidden state.
```

This is much stronger than the general phrase “check the package.”

## Typical Cases for ASSERTION with `polarity: not`

Negative assertions are especially important where the model may:

```text
- rush;
- guess;
- “help” beyond the instruction;
- silently change meaning;
- add unnecessary structure;
- move to the next stage without permission;
- hide uncertainty;
- present an intermediate result as final.
```

Typical `ASSERT.NOT` rules for Ordo:

```text
ASSERT.NOT invented_value
ASSERT.NOT skipped_gate
ASSERT.NOT implicit_approval
ASSERT.NOT hidden_freeform_rule
ASSERT.NOT unexpected_file
ASSERT.NOT unconfirmed_contract
ASSERT.NOT unresolved_conflict
ASSERT.NOT ambiguous_status
ASSERT.NOT final_output_before_validation
ASSERT.NOT example_used_as_rule
```

In v0.12, these should preferably be described as `ASSERTION`:

```yaml
assertions:
  - id: "A_NO_FINAL_OUTPUT_BEFORE_VALIDATION"
    polarity: "not"
    condition: "final_output_created_before_validation_passed"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"
```

## Negative Checks and Statuses

`ASSERTION` is closely connected to statuses.

For example, if the process status is:

```text
needs_user_decision
```

there should be a negative assertion:

```text
ASSERT.NOT continue_without_user_decision
```

If the status is:

```text
blocked_by_missing_contract
```

there should be:

```text
ASSERT.NOT generate_final_artifact
```

Otherwise, the status becomes decorative. The model appears to know that the process is blocked but may still continue.

In Ordo, status must affect allowed actions.

## Negative Checks and FREEFORM

![Nebu — thinking: FREEFORM must not hide control rules](../assets/mascots/64x64/Nebu_thinking_64x64.png)

One of the most dangerous places is FREEFORM.

FREEFORM is needed when part of the knowledge is too early or impossible to formalize fully. But it must not become storage for hidden rules.

Useful assertions for FREEFORM therefore include:

```text
ASSERT.NOT core_gate_hidden_in_freeform
ASSERT.NOT mandatory_output_hidden_in_freeform
ASSERT.NOT approval_rule_hidden_in_freeform
ASSERT.NOT business_decision_hidden_in_freeform
```

In simpler terms:

```text
An explanation may live in FREEFORM.
A control point must be formal.
```

If a rule stops the process, changes the path, defines output, or requires human confirmation, it must not exist only in FREEFORM.

## Negative Checks in Document Work

For documentation, assertions with `polarity: not` are almost mandatory.

Examples:

```text
ASSERT.NOT duplicate_section
ASSERT.NOT unresolved_placeholder
ASSERT.NOT obsolete_term
ASSERT.NOT inconsistent_alias
ASSERT.NOT missing_traceability
ASSERT.NOT markdown_link_to_internal_draft
ASSERT.NOT raw_runtime_note_in_final_document
```

They catch what an ordinary positive check often misses.

For example, a document may contain all required sections and still contain:

```text
<TODO>
<ASK_USER_LATER>
old_alias
draft only
```

The positive gate “structure is correct” will not catch this. A negative assertion will.

## Severity: When to Stop and When to Warn

Not every negative check is equally critical.

Therefore, Ordo `ASSERTION` needs severity:

```text
info
warn
block
```

For example:

```yaml
assertions:
  - id: "A_NO_TODO_IN_FINAL"
    polarity: "not"
    condition: "final_artifact_contains_todo_marker"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"

  - id: "A_NO_MINOR_STYLE_DRIFT"
    polarity: "not"
    condition: "document_contains_minor_style_inconsistency"
    phase: ["runtime"]
    method: "self_verification"
    severity: "warn"
```

The rule is simple:

```text
If the violation can make the result incorrect or dangerous — block.
If the violation only reduces quality without breaking the result — warn.
```

## Compiler Projection

In v0.12, the compiler must be able to expand an assertion into several target forms.

For example:

```yaml
assertions:
  - id: "A_NO_SKIPPED_GATE"
    polarity: "not"
    condition: "required_gate_was_skipped"
    phase: ["runtime", "test", "debug"]
    method: "mechanical"
    severity: "block"
```

The compiler may create:

```text
runtime: ASSERT.NOT required_gate_was_skipped
test:    EXPECT.NOT required_gate_was_skipped
debug:   VIOLATION.RECORD if required_gate_was_skipped is true
```

This reduces the risk that a prohibition is described in one place but forgotten in another.

## Typical Mistakes

### Mistake 1. Expressing a Prohibition Only in Words

Bad:

```text
Do not make mistakes.
```

Better:

```text
ASSERT.NOT skipped_gate
ASSERT.NOT invented_required_value
ASSERT.NOT final_output_before_validation
```

Even better in v0.12:

```yaml
assertions:
  - id: "A_NO_FINAL_OUTPUT_BEFORE_VALIDATION"
    polarity: "not"
    condition: "final_output_before_validation"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"
```

A prohibition must be checkable.

### Mistake 2. Combining Everything into One Large Gate

Bad:

```text
Check that everything is fine.
```

Better:

```text
GATE required_files_present
ASSERT.NOT unexpected_files_present
ASSERT.NOT unresolved_placeholders_present
ASSERT.NOT validation_report_missing
```

One large gate creates an illusion of control but provides no precise trace.

### Mistake 3. Making Negative Checks Too Abstract

Bad:

```text
ASSERT.NOT bad_result
```

Better:

```text
ASSERT.NOT result_contains_unconfirmed_business_decision
```

The model and runtime must understand exactly what is being checked.

### Mistake 4. Omitting the Consequence

Bad:

```yaml
assertions:
  - condition: "missing_approval"
```

Better:

```yaml
assertions:
  - id: "A_NO_MISSING_APPROVAL"
    polarity: "not"
    condition: "missing_approval"
    phase: ["runtime"]
    method: "mechanical"
    severity: "block"
    on_fail: "STOP"
```

Without a consequence, the check may become only a comment.

### Mistake 5. Forgetting Test Projection

Bad:

```text
The rule exists at runtime but is absent from the regression suite.
```

Better:

```yaml
phase: ["runtime", "test"]
```

The compiler must then create a runtime assertion and test expectation from the same source.

## Mini-Exercise

Take a simple instruction:

```text
Prepare the final document for handoff to a developer.
```

Try to list five negative checks.

For example:

```text
1. There must be no unresolved placeholders.
2. There must be no invented technical details.
3. There must be no contradiction between the task description and acceptance criteria.
4. There must be no links to intermediate drafts.
5. There must be no final status without a self-check.
```

Then rewrite them in Ordo v0.12 style:

```yaml
assertions:
  - id: "A_NO_UNRESOLVED_PLACEHOLDER"
    polarity: "not"
    condition: "unresolved_placeholder_present"
    phase: ["runtime", "test"]
    method: "mechanical"
    severity: "block"

  - id: "A_NO_INVENTED_TECHNICAL_DETAIL"
    polarity: "not"
    condition: "invented_technical_detail_present"
    phase: ["runtime", "test"]
    method: "self_verification"
    severity: "block"
```

## Short Summary

`ASSERTION` is the canonical way to describe a rule that must hold or must not be violated.

`ASSERT.NOT` is shorthand for an assertion with `polarity: not`.

An ordinary gate checks that something required has been done. `ASSERT.NOT` checks that something forbidden did not happen.

This is critical for Ordo because an AI model often fails not only by omitting an action but also by doing too much: inventing, skipping ahead, adding, hiding, mixing, or finishing prematurely.

A good Ordo program has not only a list of what must be done but also a list of what must not be done. In v0.12, this is best described once as an `ASSERTION`, and the compiler should project that rule into runtime, test, and debug representations.
