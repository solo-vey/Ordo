# Chapter 13. Status Semantics

## Why This Is Needed

In an ordinary conversation with artificial intelligence, status often looks like a minor detail.

A model may write:

```text
ready
done
can be handed off
looks correct
clarification is needed
```

At first glance, everything seems understandable. But this is not enough for a controlled process.

The problem is that such words do not always have a precise meaning. For one person, “ready” means “the draft can be read.” For another, it means “the file can be handed to a developer.” For a third, it means “all checks passed and no risks remain.”

For Ordo, this ambiguity is dangerous. If a status has no formal semantics, the model may finish a process prematurely, skip an approval gate, present a draft as a final result, or call a result “ready” without evidence.

Therefore, Ordo needs a separate language construct:

```text
STATUS.SEMANTICS
```

It defines exactly what each status means, who may set it, which gates must pass before it, and which actions are allowed afterward.

## Simple Explanation

A status is not merely a label.

![Nebu — idea: status as a controlled process position](../assets/mascots/64x64/Nebu_idea_64x64.png)

In Ordo, status is a controlled position in the process.

For example:

```text
needs_input
ready_for_analysis
analysis_in_progress
needs_approval
approved_for_generation
ready_for_handoff
blocked
```

Every status should answer several questions:

```text
1. What has already happened?
2. What has not happened yet?
3. Who is allowed to move the process into this status?
4. Which actions are now allowed?
5. Which actions are now forbidden?
6. What is the next legal status?
```

Without this, statuses are decorative words. With it, they become part of execution.

## Why Statuses Matter Specifically for an AI Model

A person often understands status from context. If an analyst says “you can proceed,” another person may clarify what exactly is allowed: continue analysis, create a file, send it to QA, or hand it to a developer.

An AI model does not interpret this reliably. It may understand the word “yes” too broadly.

For example, the user says:

```text
Yes, this option works.
```

The model may incorrectly decide:

```text
The user approved final archive generation.
```

But the user may have meant only:

```text
I like the idea, but this is not yet the final document.
```

`STATUS.SEMANTICS` is needed so such transitions do not happen automatically.

## Ordo Construct

In Ordo, a status can be described like this:

```yaml
status_semantics:
  - status: "needs_input"
    meaning: "the process waits for data or a decision from the user"
    allowed_actions:
      - "ask_question"
      - "summarize_current_state"
    forbidden_actions:
      - "generate_final_package"
      - "mark_as_ready_for_handoff"
    next_allowed_statuses:
      - "ready_for_analysis"
      - "blocked"

  - status: "ready_for_handoff"
    meaning: "the result passed mandatory gates and may be handed off"
    requires_gates:
      - "G_CONTRACT_CONFIRMED"
      - "G_OUTPUT_VALIDATED"
      - "G_SELF_CHECK_PASSED"
    allowed_actions:
      - "handoff_result"
    forbidden_actions:
      - "change_contract_without_reapproval"
```

In compiled IR, this may become:

```json
[
  {
    "op": "STATUS.DEF",
    "id": "S_NEEDS_INPUT",
    "status": "needs_input",
    "meaning": "process waits for user input or decision"
  },
  {
    "op": "STATUS.ALLOW",
    "status": "needs_input",
    "actions": ["ask_question", "summarize_current_state"]
  },
  {
    "op": "STATUS.FORBID",
    "status": "needs_input",
    "actions": ["generate_final_package", "mark_as_ready_for_handoff"]
  },
  {
    "op": "STATUS.REQUIRE.GATES",
    "status": "ready_for_handoff",
    "gates": ["G_CONTRACT_CONFIRMED", "G_OUTPUT_VALIDATED", "G_SELF_CHECK_PASSED"]
  }
]
```

The exact syntax is less important than the principle: status must be an executable rule rather than a free phrase.

## Status Lifecycle

For an Ordo program, it is useful to describe not only individual statuses but also the process lifecycle.

For example:

```text
created
→ needs_input
→ contract_ready
→ contract_confirmed
→ analysis_in_progress
→ needs_approval
→ approved_for_generation
→ generation_in_progress
→ validation_in_progress
→ ready_for_handoff
→ handed_off
```

This lifecycle shows how the process should move.

Importantly, the model must not invent transitions between statuses.

If only this is allowed:

```text
needs_approval → approved_for_generation
```

the model cannot jump directly to:

```text
needs_approval → ready_for_handoff
```

even if it feels that “everything is already clear.”

## Status Transition

A transition between statuses is a separate action.

In a simple form:

```yaml
status_transitions:
  - from: "needs_approval"
    to: "approved_for_generation"
    allowed_by:
      - "user_explicit_approval"
    requires:
      - "approval_scope_defined"
    on_missing_requirement: "STOP"
```

This means the model cannot simply say “it seems approved.” There must be explicit confirmation or another allowed condition.

In Ordo, it is useful to distinguish:

```text
model_can_set
user_must_set
runtime_can_set
external_system_can_set
```

For example:

```yaml
status: "contract_confirmed"
can_be_set_by:
  - "user"
forbidden_for:
  - "model_without_explicit_approval"
```

This is especially important in processes where the model assists but must not make business decisions on behalf of a person.

## Statuses and Gates

A status must not be set without gates.

Bad:

```text
Model: everything is checked, status ready_for_handoff.
```

Better:

```yaml
set_status: "ready_for_handoff"
requires_gates:
  - "G_REQUIRED_FILES_PRESENT"
  - "G_NO_UNRESOLVED_PLACEHOLDERS"
  - "G_CONSISTENCY_CHECK_PASSED"
  - "G_HANDOFF_NOTE_PRESENT"
```

Now status is not the model's opinion. It is the result of passing control points.

If even one gate fails, the status cannot be set.

```text
G_CONSISTENCY_CHECK_PASSED = failed
→ ready_for_handoff is forbidden
```

This is how Ordo reduces the risk of a premature “done.”

## Statuses and ASSERT.NOT

Negative checks can also be attached to statuses.

For example:

```yaml
status: "ready_for_handoff"
assert_not:
  - "unresolved_placeholders_present"
  - "missing_validation_report"
  - "unconfirmed_assumption_present"
  - "freeform_without_binding"
```

This means the process cannot call itself ready while forbidden conditions remain.

For a final status, negative checks are often especially important:

```text
no unfilled places
no invented decisions
no invisible assumptions
no unvalidated documents
no unexplained FREEFORM
```

## Statuses and User Answers

![Nebu — attention: a short answer applies only within the current node](../assets/mascots/64x64/Nebu_attention_64x64.png)

One of the most important problems in AI-model work is interpreting short user answers.

The user may write:

```text
yes
ok
works
next
you can
agreed
```

Without `STATUS.SEMANTICS`, the model may interpret this too broadly.

Ordo must require that a short user answer be interpreted only within the current node or current gate.

For example, if the current question was:

```text
Select option A, B, or C?
```

and the user answers:

```text
A
```

this does not mean:

```text
the user approved the final package
```

It means only:

```text
the user selected option A in the current node
```

Therefore, status in Ordo must be connected to the current node, current gate, and current question.

## Example: Guided Intake

Imagine that the model conducts guided intake for a new historical event.

Possible statuses:

```yaml
statuses:
  - "intake_started"
  - "path_selected"
  - "event_alias_confirmed"
  - "source_row_confirmed"
  - "values_confirmed"
  - "qa_scope_confirmed"
  - "package_ready_for_generation"
  - "package_generated"
  - "package_validated"
  - "package_ready_for_handoff"
```

Allowed transitions can be defined for each status:

```yaml
transitions:
  - from: "intake_started"
    to: "path_selected"
    requires: ["path_decision_answered"]

  - from: "path_selected"
    to: "event_alias_confirmed"
    requires: ["alias_confirmed_by_user"]

  - from: "package_generated"
    to: "package_validated"
    requires: ["self_check_executed", "validation_report_created"]

  - from: "package_validated"
    to: "package_ready_for_handoff"
    requires: ["no_blocking_validation_errors"]
```

Now the model does not merely “follow the conversation.” It moves through a controlled status map.

## Example: A Document

For document preparation, statuses may be:

```text
draft_requested
structure_confirmed
content_drafted
content_reviewed
rendered_artifact_created
rendered_artifact_validated
ready_to_share
```

It is important not to confuse:

```text
content_drafted
```

with:

```text
ready_to_share
```

An ordinary model may say “done” after creating the text. In Ordo, the text is not ready if the final artifact has not been validated.

For example:

```yaml
status: "ready_to_share"
requires:
  - "content_reviewed"
  - "rendered_artifact_created"
  - "rendered_artifact_validated"
  - "download_link_available"
```

This is especially important for PDFs, DOCX files, presentations, archives, and document packages.

## Draft, Final, and Handoff

One of the main reasons to introduce statuses is to separate three different states:

```text
draft
final
handoff_ready
```

They are not the same.

`draft` means:

```text
the text or structure has been created but may still be incomplete
```

`final` means:

```text
the content is considered complete within the current contract
```

`handoff_ready` means:

```text
the result is not only complete but also validated, packaged, and ready for transfer
```

Ordo must not substitute one status for another.

For example:

```text
final_content != handoff_ready_package
```

Final text may be ready while the file remains unvalidated. Or a package may be assembled while the validation report still contains errors. In such cases, `handoff_ready` is forbidden.

## Status Report

An Ordo process should be able to show status not only as a word but as a short report.

For example:

```yaml
status_report:
  current_status: "needs_approval"
  current_node: "N_APPROVE_PACKAGE_SCOPE"
  completed_gates:
    - "G_PATH_SELECTED"
    - "G_ALIAS_CONFIRMED"
  pending_gates:
    - "G_PACKAGE_SCOPE_APPROVED"
  blocked_actions:
    - "generate_final_archive"
  next_allowed_actions:
    - "ask_package_scope_approval"
```

Such a report is useful for the user, the runtime, and the next model that may continue the process.

It also reduces context loss in long conversations.

## Statuses and Trace

![Nebu — thinking: status must leave a trace](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Statuses must leave a trace.

It is not enough to have only the current status. A transition history is needed:

```yaml
trace_source: "model_self_report"
status_trace:
  - from: "needs_input"
    to: "contract_ready"
    reason: "all mandatory intake fields collected"
    evidence: ["E_INPUT_FIELDS_COMPLETE"]

  - from: "contract_ready"
    to: "contract_confirmed"
    reason: "user explicitly approved contract"
    evidence: ["E_USER_APPROVAL_2026_07_05"]
```

This answers:

```text
why is the process in this status now?
who or what moved it here?
what evidence supports the transition?
```

For Ordo, this is essential because without trace, status again becomes merely a model claim.

## Typical Mistakes

### Mistake 1. Using Vague Statuses

Bad:

```text
ok
ready
done
almost_done
good
```

Better:

```text
contract_confirmed
content_drafted
validation_passed
ready_for_handoff
```

A status must describe a concrete process state.

### Mistake 2. Failing to Separate Approval and Execution

Bad:

```text
approved
```

What exactly was approved: the idea, structure, contract, generation, or final file?

Better:

```text
contract_approved
package_scope_approved
generation_approved
handoff_approved
```

### Mistake 3. Allowing the Model to Set Final Statuses by Itself

Bad:

```yaml
status: "ready_for_handoff"
can_be_set_by: ["model"]
```

Better:

```yaml
status: "ready_for_handoff"
can_be_set_by: ["runtime"]
requires_gates:
  - "G_SELF_CHECK_PASSED"
  - "G_RENDERED_ARTIFACT_VALIDATED"
  - "G_NO_BLOCKING_ERRORS"
```

Or, if there is no runtime:

```yaml
can_be_set_by: ["model_after_required_trace"]
```

but only with a mandatory gate report.

### Mistake 4. Failing to Describe Allowed Transitions

Bad:

```text
status may be any value from the list
```

Better:

```yaml
from: "needs_approval"
to: "approved_for_generation"
requires: ["explicit_user_approval"]
```

Statuses without transitions are a dictionary. Statuses with transitions are a process.

### Mistake 5. Confusing Status and Result

```text
status = ready_for_handoff
```

is not the handoff itself. It is only permission to perform the handoff.

Likewise:

```text
status = validation_passed
```

is not a validation report. It is the result of passing a validation gate, which must have evidence.

## Mini-Exercise

Take any process you often delegate to an AI model.

For example:

```text
Prepare a Jira task.
```

Try to describe statuses:

```text
request_received
problem_context_collected
acceptance_criteria_drafted
qa_scope_drafted
pm_level_review_needed
ready_for_jira_copy
```

Then answer for every status:

```text
1. What does this status mean?
2. Who may set it?
3. Which gates are required before it?
4. Which actions are allowed after it?
5. Which actions are forbidden after it?
6. Which next status is allowed?
```

You will see that even a simple process becomes much more controlled.

## Short Summary

`STATUS.SEMANTICS` defines exactly what statuses mean in an Ordo program.

A status in Ordo is not merely the word “ready” or “done.” It is a formal process state with rules, allowed actions, prohibitions, transitions, gates, and evidence.

Well-defined statuses protect a process from premature completion, incorrect interpretation of short user answers, hidden transitions, and confusion between a draft and a final handoff.

If a `Gate` answers “may we move forward?”, then `STATUS.SEMANTICS` answers “where exactly are we in the process, and what are we allowed to do next?”

<!-- REVIEWED: chapter 13; Nebu markers checked -->
