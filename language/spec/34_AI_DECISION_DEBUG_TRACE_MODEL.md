# AI Decision Debug Trace Model v1

## Purpose

The execution trace must make every decision-bearing node understandable from
recorded facts, not from guesses made after the run. A node event therefore
records the exact question or model message shown to the analyst, the analyst
response, the selected transition, the relevant rules and evidence, and a
bounded explanation of the decision.

## Required decision record

Each decision-bearing interaction uses a `decision_record` with these fields:

```yaml
decision_record:
  node_id: N_CLASSIFY
  question_text: "Has the database schema changed?"
  question_ref: question.schema.v3
  question_context_digest: sha256:...
  analyst_response: "No schema changes."
  selected_transition: N_APPROVE
  applicable_rules:
    - schema_unchanged
  evidence_refs:
    - input.schema
    - artifact.schema
  state_before_ref: snapshot.16
  state_after_ref: snapshot.17
  state_diff:
    status: [pending, approved]
  replay_anchor: decision.1
  reason_code: required_fields_complete
  decision_summary: "The required schema fields are unchanged, so the approval path was selected."
  summary_kind: bounded_redacted_model_report
  hidden_chain_of_thought_persisted: false
```

`question_text` and `analyst_response` are observable interaction facts. The
context digest and question reference identify the prompt/version context that
produced a dynamic question without duplicating the entire prompt context in
every event.

## Decision summary boundary

`decision_summary` may be detailed enough to explain the selected path and the
evidence used. It is a bounded, redacted model report and must be treated as an
explanatory hypothesis, not as authoritative proof. The trace must never store
hidden chain-of-thought, private reasoning, scratchpads, or internal model
monologues. The authoritative record is the rendered interaction, input,
rules, evidence, transition, and state change.

Summaries must be filtered for secrets and personal data before persistence.
The runtime rejects empty or unbounded summaries and marks the record with
`summary_kind: bounded_redacted_model_report`.

## Capture and replay

The existing `minimal`, `standard`, `full`, and `audit` capture levels remain
valid. Decision interactions are captured wherever the `decision` event class
is enabled. A replay anchor identifies the node/state boundary from which a
deterministic, re-evaluated, simulated, or audit-only replay can start.

Replay consumers must distinguish observed facts, the model report, and later
reconstruction. This model changes observability only; it does not change
playbook graph semantics or selected transition rules.

## Validation requirements

The CLI/runtime contract must verify that decision records have a node, exact
question text, analyst response, selected transition, and non-empty bounded
summary. Tests must cover persistence, redaction, integrity/checksum
preservation, replay anchors, and rejection of empty or overlong summaries.
