# Chapter 5. State: Process Memory

![Nebu — idea](../assets/mascots/64x64/Nebu_idea_64x64.png)

## 5.1. Why Ordo needs State

A long conversation is not the same thing as explicit process memory.

A model may see the conversation history, but that does not guarantee that every confirmed fact, open question, selected path, or blocker will remain semantically stable throughout execution.

A process therefore needs `State`.

State is the explicit memory of the current run.

It answers:

```text
Where are we?
What is already known?
What has been confirmed?
What is still proposed?
What remains open?
What blocks completion?
```

Without State, the model must reconstruct the process from conversation text every time.

With State, the important execution facts are explicit.

## 5.2. How State differs from Context

Context is information available to the process.

State is information about the current execution.

For example:

```yaml
context:
  source_document: incident_report_17
```

This is a source.

But:

```yaml
state:
  source_document_reviewed: true
  severity: high
  severity_status: confirmed
```

describes what has happened in the current run.

A simple distinction is:

```text
Context = what we work with.
State   = what the process currently knows and where it is.
```

## 5.3. A simple State example

Consider a guided intake process.

```yaml
state:
  current_node: N3
  selected_path: Path_1
  task_type: incident
  business_goal:
    value: restore_service
    status: confirmed
  acceptance_criteria:
    value: null
    status: missing
  open_questions:
    - acceptance_criteria
  blockers:
    - acceptance_criteria_missing
```

A model reading this state does not need to infer whether the business goal was confirmed.

It is explicit.

The model also sees that the process is at `N3`, follows `Path_1`, and cannot complete because acceptance criteria are missing.

## 5.4. `STATE.SCHEMA`

A process should define the shape of its state.

Conceptually:

```yaml
state_schema:
  current_node:
    type: string
    required: true

  selected_path:
    type: string
    nullable: true

  confirmed_contracts:
    type: array

  assumptions:
    type: array

  open_questions:
    type: array

  blockers:
    type: array
```

In Ordo, `STATE.SCHEMA` exists to make process memory explicit and validatable.

The schema answers:

```text
Which state fields exist?
Which values are allowed?
Which fields are required?
Which statuses are valid?
```

This is important because uncontrolled state can become as chaotic as an uncontrolled prompt.

## 5.5. State as protection against repeated questions

Imagine that the user has already confirmed:

```text
The request is an incident.
```

If the process writes:

```yaml
state:
  request_type:
    value: incident
    status: confirmed
```

the next node can see that the question has already been answered.

The process should not ask it again unless a specific transition invalidates or reopens that field.

This improves user experience and process consistency.

State is therefore not only technical memory. It is also a mechanism for respecting what the user has already told the process.

## 5.6. State as protection against premature results

Suppose the process must not generate a final Jira task until the business goal and acceptance criteria are confirmed.

State may contain:

```yaml
state:
  business_goal:
    status: confirmed
  acceptance_criteria:
    status: missing
  handoff:
    allowed: false
```

A gate can check:

```text
business_goal.status == confirmed
AND
acceptance_criteria.status == confirmed
```

Until the condition is satisfied, the final handoff remains blocked.

Without State, the model may decide that it has “enough information.”

With State, completion conditions can be evaluated explicitly.

![Nebu — thinking](../assets/mascots/64x64/Nebu_thinking_64x64.png)

## 5.7. State and statuses

Values in a process often need status, not only content.

For example:

```yaml
state:
  event_type:
    value: address_change
    status: proposed
```

Later:

```yaml
state:
  event_type:
    value: address_change
    status: confirmed
```

Useful status categories may include:

```text
missing
proposed
confirmed
rejected
deprecated
blocked
```

The exact status set depends on the contract.

The important principle is that a value and the authority of that value are different things.

A plausible value is not automatically a confirmed value.

## 5.8. Assumption ledger as part of State

Models are good at filling gaps. In governed processes, invisible gap-filling is dangerous.

An assumption ledger makes assumptions explicit.

Example:

```yaml
state:
  assumptions:
    - id: A1
      statement: "The change affects only the primary address."
      status: proposed
      evidence_refs:
        - user_message_12
```

The process can later:

```text
confirm the assumption;
reject it;
replace it with a fact;
block completion until it is resolved.
```

The main rule is:

```text
An assumption may help the process move,
but it must not silently become a confirmed contract.
```

## 5.9. State and open questions

Open questions should also be explicit.

Example:

```yaml
state:
  open_questions:
    - id: Q1
      field: acceptance_criteria
      blocking: true
    - id: Q2
      field: optional_label
      blocking: false
```

This allows the process to distinguish between:

```text
a question that must be resolved before completion;
a question that may remain open;
a question that has already been answered.
```

A final result can then report unresolved non-blocking questions while refusing completion when blocking questions remain.

## 5.10. State and traceability

State tells us the current situation.

Trace tells us how we arrived there.

For example:

```text
State:
event_type = address_change
status = confirmed
```

The execution trace may show:

```text
event 12: user proposed address_change
event 13: validation passed
event 14: user confirmed
event 15: state changed from proposed to confirmed
```

These concepts should not be confused.

```text
State = current process memory.
EXECUTION_TRACE = history of process execution.
```

Together, they make the run both operable and explainable.

## 5.11. State in compiled IR

In compiled IR, state structure should remain machine-readable.

For example:

```json
{
  "state": {
    "current_node": "N3",
    "selected_path": "Path_1",
    "fields": {
      "business_goal": {
        "value": "restore_service",
        "status": "confirmed"
      },
      "acceptance_criteria": {
        "value": null,
        "status": "missing"
      }
    },
    "open_questions": [
      "acceptance_criteria"
    ],
    "blockers": [
      "acceptance_criteria_missing"
    ]
  }
}
```

The runtime or model should not need to parse a narrative paragraph to determine whether handoff is allowed.

![Nebu — attention](../assets/mascots/64x64/Nebu_attention_64x64.png)

## 5.12. Typical State mistakes

### Mistake 1. Not maintaining State explicitly

If important facts exist only in chat history, the process has no stable execution memory.

### Mistake 2. Mixing Context and State

A source document is Context.

The fact that the document has been reviewed and accepted is State.

### Mistake 3. Not distinguishing `proposed` and `confirmed`

This is one of the most dangerous mistakes in AI-assisted processes.

A model suggestion may be reasonable and still require confirmation.

### Mistake 4. Not preserving blockers

If a blocker is only mentioned in prose, the process may later forget it.

Blockers should be explicit.

### Mistake 5. Not clearing assumptions before the final result

A process should know which assumptions remain unresolved.

Where the contract requires confirmed facts, unresolved assumptions must block completion.

## 5.13. A practical State template for an Ordo process

A useful starting structure is:

```yaml
state:
  current_node: START
  selected_path: null

  fields: {}

  confirmed_contracts: []

  assumptions: []

  open_questions: []

  blockers: []

  approvals: []

  outputs:
    status: not_started

  handoff:
    status: draft
    allowed: false
```

A real process will extend this structure.

The important thing is that process memory has an explicit home.

## 5.14. Short chapter summary

State is the explicit memory of an Ordo run.

It records:

```text
current position;
selected path;
known values;
value statuses;
confirmed contracts;
assumptions;
open questions;
blockers;
approvals;
output and handoff readiness.
```

State differs from Context.

Context contains information available to the process.

State describes the current execution.

State also differs from `EXECUTION_TRACE`.

State tells us where the process is now.

Trace tells us how it got there.

## Mini-exercise

Take any process in which the model must ask several questions before producing a result.

For example:

```text
Prepare a Jira task from a user's description.
```

Try to describe State:

```yaml
state:
  current_node: START
  task_type: unknown
  business_goal: missing
  acceptance_criteria: missing
  out_of_scope: missing
  assumptions: []
  open_questions: []
  blockers: []
  handoff:
    status: draft
    allowed: false
```

Then answer:

```text
1. Which fields must be confirmed before the final task?
2. Which fields may be proposed?
3. Which open questions block handoff?
4. Which gate prevents the final document from being created too early?
```

---

---

## 5.11. Revision-bound evidence and invalidation

State must not merely say that an artifact was validated or confirmed. It must record exactly which artifact revision was validated or confirmed.

```yaml
artifact_state:
  artifact_id: "playbook_package"
  revision: 7
  sha256: "..."

validation_evidence:
  target_revision: 7
  target_sha256: "..."
  status: passed
```

When an upstream artifact changes, downstream evidence that depended on the previous revision becomes stale. Ordo must invalidate it explicitly rather than silently carrying it forward.

```text
upstream revision changes
→ dependent confirmation becomes invalid
→ dependent validation becomes invalid
→ completion is blocked
→ new evidence is required
```

A safe runtime keeps an append-only invalidation log and increases `state_version` after every state mutation. Old evidence is historical information, not authorization for a new revision.
