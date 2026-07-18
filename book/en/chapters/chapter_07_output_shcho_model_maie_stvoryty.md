# Chapter 7. Output: What the Model Must Create

## 7.1. Why Ordo Describes Output Separately

A process can be executed correctly and still end with the wrong artifact.

For example, the model may correctly identify the path, collect the required contracts, and pass the checks, but then return a short chat summary instead of the document package expected by the next process.

That is why Ordo describes output explicitly.

`OUTPUT.DEF` answers:

```text
What exactly must be created?
In what form?
When is creation allowed?
How can the result be checked?
```

![Nebu — idea: Output is an explicit process artifact](../assets/mascots/64x64/Nebu_idea_64x64.png)

Output is not simply “the model's answer.” It is a process artifact with a contract.

---

## 7.2. Output Is Not Only a Text Reply

A model may create many kinds of output:

```text
a chat response;
a document;
a set of documents;
a JSON report;
a YAML specification;
an archive;
a blocked handoff status.
```

For example:

```json
{
  "op": "OUTPUT.DEF",
  "id": "OUT_HISTORY_EVENT_PACKAGE",
  "kind": "artifact_set",
  "required": [
    "01_HISTORY_EVENT_PASSPORT_<ALIAS>.md",
    "02_JIRA_TASK_<ALIAS>.md",
    "05_QA_PACKAGE_<ALIAS>.md"
  ]
}
```

If the process only says “prepare the result,” the model may decide that one short walkthrough is sufficient.

The output contract says that a defined set of files is required.

---

## 7.3. Output Must Be Connected to a Terminal Path

In a decision-tree process, different terminal paths may have different outputs.

For example, in a support process:

```text
incident ready → INCIDENT_REPORT.md + CUSTOMER_REPLY.md
incident needs triage → INCIDENT_TRIAGE_NOTE.md
change ready → CHANGE_BRIEF.md + ACCEPTANCE_CHECKLIST.md
change unclear → CHANGE_CLARIFICATION_NOTE.md
```

This means the output is not always the same. It depends on the selected path.

In Ordo, this can be described as:

```yaml
terminal_outputs:
  T_INCIDENT_READY:
    outputs:
      - INCIDENT_REPORT.md
      - CUSTOMER_REPLY.md

  T_INCIDENT_NEEDS_TRIAGE:
    outputs:
      - INCIDENT_TRIAGE_NOTE.md

  T_CHANGE_READY:
    outputs:
      - CHANGE_BRIEF.md
      - ACCEPTANCE_CHECKLIST.md

  T_CHANGE_NEEDS_CLARIFICATION:
    outputs:
      - CHANGE_CLARIFICATION_NOTE.md
```

This protects the process from creating the wrong document for the correct path.

---

## 7.4. Output May Be Allowed or Blocked

Not every output may be created at any time.

For example, a final archive must not be created while contracts remain unconfirmed.

Output therefore needs readiness conditions.

Example:

```json
{
  "op": "OUTPUT.DEF",
  "id": "OUT_FINAL_ARCHIVE",
  "kind": "zip_archive",
  "allowed_when": [
    "path_confirmed",
    "mandatory_contracts_confirmed",
    "required_documents_approved",
    "validation_status_go"
  ],
  "blocked_when": [
    "unresolved_mandatory_contract",
    "proposed_contract_used_as_confirmed",
    "approval_missing",
    "validation_status_no_go"
  ]
}
```

![Nebu — attention: Output is allowed only after gates](../assets/mascots/64x64/Nebu_attention_64x64.png)

This is important: output defines not only “what to create,” but also “when creation is allowed.”

---

## 7.5. Draft Output and Final Output

In real work, the model often needs to create a draft first.

For example:

```text
first a draft passport in chat;
then user approval;
then a draft Jira task;
then approval;
then a QA package;
then an automation spec;
and only after approvals — the final archive.
```

This means there are different output levels:

```text
draft output;
review output;
approved output;
final output.
```

In Ordo, these levels should be explicit.

For example:

```yaml
outputs:
  passport_draft:
    file: "01_HISTORY_EVENT_PASSPORT_<ALIAS>.md"
    status: draft
    requires_approval: true

  passport_final:
    file: "01_HISTORY_EVENT_PASSPORT_<ALIAS>.md"
    status: approved
    allowed_when:
      - passport_approval_passed
```

Without this distinction, the model may confuse a draft with a final document.

---

## 7.6. Output and Template

In many Ordo processes, output is created from a template rather than from scratch.

For example:

```text
A Jira task must contain Summary, Context, Acceptance criteria, Out of scope, and QA reference data.
```

Then `OUTPUT.DEF` alone is not enough. The output must be connected to a template.

This is a profile-level construct:

```text
TEMPLATE.BIND
```

Example:

```json
{
  "op": "TEMPLATE.BIND",
  "output": "02_JIRA_TASK_<ALIAS>.md",
  "template": "templates/TEMPLATE_JIRA_TASK.md",
  "required_sections": [
    "Summary",
    "Context",
    "Acceptance criteria",
    "Out of scope",
    "QA reference data",
    "Test coverage"
  ]
}
```

`OUTPUT.DEF` says that the file must exist.

`TEMPLATE.BIND` says which structure must be used to create it.

---

## 7.7. Output Must Be Verifiable

If output cannot be checked, the model may report completion even when the artifact is incomplete.

A weak output contract:

```text
Create a good QA package.
```

What does “good” mean? For the model, it may mean a short summary. For a tester, it may mean a complete step-by-step runbook.

A better output contract:

```yaml
output:
  file: "05_QA_PACKAGE_<ALIAS>.md"
  required_for_each_executable_tc:
    - goal
    - preconditions
    - source_lookup_before_action
    - preflight_restore
    - rest_action
    - source_lookup_after_action
    - changerecord_lookup_or_expected_absence
    - history_processing_step
    - history_event_lookup_or_expected_absence
    - change_errors_lookup
    - rollback
    - post_rollback_source_lookup
    - expected_result
    - diagnostics
```

Now the output can be checked.

The model cannot replace the required structure with “see the general flow.”

---

## 7.8. Output May Be Absent — and That Is Also a Result

Sometimes the correct result is not to create a document.

If mandatory contracts are not confirmed, the correct behavior is not to invent a package but to stop.

The output may then be:

```json
{
  "op": "OUTPUT.DEF",
  "id": "OUT_BLOCKED_STATUS",
  "kind": "handoff_status",
  "status": "blocked_requires_confirmation",
  "include": [
    "missing_contracts",
    "open_questions",
    "next_required_action"
  ]
}
```

![Nebu — thinking: a blocked handoff is also a result](../assets/mascots/64x64/Nebu_thinking_64x64.png)

This is an important idea.

In Ordo, a result may be not only a completed artifact but also an honest blocked handoff.

It is better to say:

```text
The package cannot be finalized because HistoryEvent.item.values has not been confirmed.
```

than to create a polished but incorrect document.

---

## 7.9. Output and Handoff

Output is what is created.

Handoff is how the process passes the result onward.

For example, the output may be a set of files, while the handoff is a short status message:

```text
Status: ready_for_review
Created: passport draft, Jira draft, QA draft
Blockers: automation runner contract not confirmed
Next action: approve the QA package
```

In Ordo, these concepts should remain separate.

`OUTPUT.DEF` describes the artifact.

`HANDOFF.EMIT` describes the transfer of status to the user or the next process.

Example:

```json
{
  "op": "HANDOFF.EMIT",
  "include": [
    "status",
    "created_outputs",
    "gate_report",
    "open_questions",
    "next_action"
  ]
}
```

---

## 7.10. Typical Output Mistakes

The first mistake is describing output too broadly.

```text
Create the package.
```

The second is failing to say how many files must exist.

The third is failing to distinguish draft from final.

The fourth is failing to bind output to a template.

The fifth is failing to define readiness conditions.

The sixth is assuming that because the model wrote something, the output is already valid.

The seventh is failing to provide a blocked output.

In complex processes, a correct “I cannot finalize because...” is often more valuable than an incorrect “Done.”

---

## 7.11. Short Chapter Summary

`OUTPUT.DEF` defines exactly what the model must create.

Output may be:

```text
a chat response;
a document;
a set of documents;
a JSON report;
a YAML specification;
an archive;
a blocked handoff status.
```

A good output contract answers:

```text
what is being created;
in which format;
from which template;
when creation is allowed;
what blocks creation;
how the result is checked;
whether the result is draft, review, or final.
```

The main principle is:

```text
A result must be not merely polished, but allowed, structured, and verifiable.
```

---

## Mini-Exercise

Take the task:

```text
The model must prepare a document for handoff to a developer.
```

Describe `OUTPUT.DEF`:

```yaml
output:
  id: OUT_DEVELOPER_HANDOFF
  kind: document
  file_name: "IMPLEMENTATION_PROMPT.md"
  required_sections:
    - goal
    - context
    - files_to_check
    - required_changes
    - what_not_to_change
    - tests
    - acceptance_criteria
  status: draft
  allowed_when:
    - business_contract_confirmed
  blocked_when:
    - missing_acceptance_criteria
    - unresolved_scope
```

Then answer:

```text
1. Which sections are mandatory?
2. What blocks creation of the final version?
3. Which template is required?
4. How do we verify that the rendered document is not empty?
```

---

<!-- REVIEWED: chapter 07; Nebu markers checked -->
