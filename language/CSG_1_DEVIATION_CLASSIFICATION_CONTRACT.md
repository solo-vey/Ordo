# CSG-1 — Deviation Classification Contract

**Status:** normative integration artifact  
**Parent contract:** `ORDO-CAP-CSG-001`

## 1. Rule

A message that does not directly satisfy the active question MUST be classified before any process-state mutation.

Canonical operation:

```text
DEVIATION.CLASSIFY
```

Classification is an interaction-control decision. It MUST NOT be used as permission to infer missing business data.

## 2. Canonical taxonomy

| Classification | Meaning | Default action | State mutation |
|---|---|---|---|
| `answer_to_active_question` | valid answer to the active question | `accept_answer` | allowed by node contract |
| `clarification` | asks to explain the active step/question | `clarify_active_step` | no |
| `correction` | corrects previously supplied process data | `apply_correction` | controlled |
| `backtrack_request` | requests return to an earlier node | `backtrack` | controlled |
| `requirement_change` | changes contract, scope, or intended output | `reopen_contract` | controlled |
| `pause_request` | requests temporary suspension | `pause_process` | process-control only |
| `resume_request` | resumes a paused run | `resume_process` | process-control only |
| `exit_request` | requests controlled termination | `exit_process` | terminal transition only |
| `process_meta_question` | asks about status, rules, or next step | `answer_process_meta` | no |
| `related_context` | supplies relevant context not yet accepted as the active answer | `register_related_context` | non-confirming only |
| `unrelated_topic` | outside declared process scope | `redirect` | forbidden |
| `unsafe_or_emergency_message` | safety/error condition with priority | `bypass_for_safety` | guard bypass |
| `unclassifiable_input` | cannot be classified safely | `request_classification_clarification` | forbidden |

## 3. Classification precedence

The classifier MUST evaluate candidates in this order:

```text
1. unsafe_or_emergency_message
2. exit_request / pause_request / resume_request
3. correction / backtrack_request / requirement_change
4. clarification / process_meta_question
5. answer_to_active_question
6. related_context
7. unrelated_topic
8. unclassifiable_input
```

Higher-precedence classes protect safety and explicit process-control intent from being incorrectly redirected.

## 4. Active-answer rule

`answer_to_active_question` is valid only when the message satisfies the active question's answer contract.

Semantic similarity alone is insufficient.

The classifier SHOULD use:

```text
active node
active question
expected answer type
allowed answer values
normalization rules
current process state
declared process scope
```

A message MAY contain additional text and still be an active answer if the required answer can be resolved without inventing missing data.

## 5. Correction versus requirement change

Use `correction` when the user changes a previously supplied value while preserving the process contract.

Use `requirement_change` when the user changes:

```text
process goal
required output
scope boundary
mandatory constraint
selected operating policy
```

A requirement change MUST reopen affected contract checks and dependent gates.

## 6. Related context

`related_context` MUST NOT automatically complete the active node.

It may be registered as non-confirmed context.

Example:

```yaml
classification: related_context
state_mutation_allowed: false
action: register_related_context
```

If the context can satisfy the active question, the runtime must reclassify it as `answer_to_active_question` before confirming state.

## 7. Ambiguity rule

When two classifications remain plausible and choosing the wrong one could mutate confirmed state, change path, or terminate/suspend the run, the classifier MUST choose:

```text
unclassifiable_input
```

and request clarification.

The classifier MUST NOT resolve high-impact ambiguity by guessing.

## 8. State mutation matrix

```text
answer_to_active_question   → node contract decides
clarification               → forbidden
correction                  → controlled correction flow
backtrack_request           → controlled rollback flow
requirement_change          → contract reopen flow
pause_request               → process-control transition only
resume_request              → process-control transition only
exit_request                → terminal transition only
process_meta_question       → forbidden
related_context             → non-confirming context only
unrelated_topic             → forbidden
unsafe_or_emergency_message → scope guard bypass
unclassifiable_input        → forbidden
```

## 9. Required record

```yaml
DEVIATION.CLASSIFY:
  message_ref: "MSG-104"
  active_node_ref: "N_CONFIRM_SOURCE_FIELD"
  active_question_ref: "Q_SOURCE_FIELD"
  classification: "unrelated_topic"
  confidence: "high"
  matched_scope_evidence: []
  classification_reason: "message does not address active question or declared process scope"
  state_mutation_allowed: false
  action: "redirect"
  trace_required: true
```

## 10. Diagnostics

Compiler/runtime diagnostics:

```text
CSG001_UNKNOWN_CLASSIFICATION
CSG002_MISSING_ACTIVE_CONTEXT
CSG003_ILLEGAL_STATE_MUTATION
CSG004_SAFETY_CLASSIFIED_AS_DEVIATION
CSG005_CONTROL_INTENT_REDIRECTED
CSG006_AMBIGUOUS_HIGH_IMPACT_CLASSIFICATION
CSG007_RELATED_CONTEXT_CONFIRMED_DIRECTLY
CSG008_ACTIVE_ANSWER_CONTRACT_NOT_CHECKED
```

`CSG003`, `CSG004`, and `CSG005` are blocking.

## 11. Trace contract

Classification MUST emit:

```text
conversation.deviation.detected
conversation.deviation.classified
```

The classification trace must record the selected class, action, active node, state-mutation permission, and confidence.

It MUST NOT contain private chain-of-thought. `classification_reason` is a concise operational reason.

## 12. Minimum regression set

Required cases:

```text
valid active answer
active answer with harmless extra text
clarification
correction
backtrack
requirement change
pause
resume
exit
process meta-question
related context
unrelated topic
safety bypass
ambiguous high-impact input
unclassifiable input
```

Required invariants:

```text
unrelated_topic cannot mutate state
unclassifiable_input cannot mutate state
related_context cannot directly confirm state
safety cannot be redirected by CSG
explicit control intent cannot be redirected as unrelated
high-impact ambiguity cannot be guessed
```
