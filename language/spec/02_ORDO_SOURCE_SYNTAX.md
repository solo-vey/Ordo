# 02. Ordo Source Syntax

Ordo Source — це читабельний YAML/Markdown-oriented шар, з якого компілятор формує Semantic JSON IR.

## Canonical source shape

```yaml
program:
  id: example.program
  ordo_version: "0.12"
  control_level: standard
  execution_mode: chat_internal

intent:
  goal: "..."

contract:
  output_type: "..."

state:
  schema:
    current_node: string
    output_allowed: boolean

nodes:
  - id: N1
    question: "..."
    allowed_answers: [yes, no]
    on_unmatched_input:
      action: CLARIFY.REQUEST
      strategy: rephrase_and_narrow
      max_attempts: 2
      on_exhausted:
        action: escalate_to_human

gates:
  - id: G1
    method: mechanical
    trust_class: deterministic
    assert: FIELD_PRESENT
    source: state.contract

assertions:
  - id: A_NO_FINAL_OUTPUT_BEFORE_GATE
    polarity: not
    condition: final_output_created_before_required_gates
    phase: [runtime, test]
    severity: block
```

## Local IDs vs compiled IDs

У Source дозволені локальні ID: `G1`, `N1`, `A1`. У compiled IR вони мають бути розгорнуті у namespaced IDs.

```text
Source: G1
IR: domain_pack.history_event.G1
```


## EXECUTION_TRACE source block

A program MAY declare a top-level `execution_trace:` block. Its canonical structure is defined by `schemas/execution_trace_schema.yaml`. New source MUST NOT introduce new event types outside the versioned registry.
