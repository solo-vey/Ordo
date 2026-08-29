# 03. Semantic JSON IR

Semantic JSON IR — поточний основний формат compiled Ordo-програми. У Process Rail моделі він є машинозчитуваною опорою для AI Ordo Developer / AI Ordo Executor, runner-а і валідатора.

## Required IR metadata

```json
{
  "ordo_version": "0.12",
  "program_id": "example.program",
  "control_level": "standard",
  "execution_mode": "chat_internal"
}
```

## Example op stream

```json
[
  {
    "op": "PROGRAM.DEF",
    "id": "program.example",
    "ordo_version": "0.12",
    "control_level": "standard",
    "execution_mode": "chat_internal"
  },
  {
    "op": "GATE.DEF",
    "id": "program.example.G_CONTRACT_PRESENT",
    "source_local_id": "G1",
    "method": "mechanical",
    "trust_class": "deterministic",
    "assert": "FIELD_PRESENT",
    "source": "contract"
  },
  {
    "op": "ASSERTION.DEF",
    "id": "program.example.A_NO_FINAL_OUTPUT_BEFORE_GATE",
    "polarity": "not",
    "condition": "final_output_created_before_required_gates",
    "phase": ["runtime", "test"],
    "severity": "block"
  }
]
```

## IR rule

Compiled IR MUST NOT contain unresolved local IDs for objects that may appear in trace, gate report, improvement records or coverage reports.


## Process Rail fields

Після M26–M30 Semantic JSON IR має підтримувати не тільки op stream, а й семантику Process Rail:

```json
{
  "process_rail": {},
  "state_schema": {},
  "conversation_semantics": {},
  "backtracking_rules": [],
  "tool_hooks": [],
  "human_explanation_policy": {},
  "output_contracts": []
}
```

Ці поля не роблять IR повністю детермінованим wizard-ом. Вони дають AI стабільну карту процесу, а deterministic helper tools — можливість перевіряти механічні частини стану, gates і переходів.

## M52: Two-tier rendering metadata

Semantic JSON IR may describe output rendering through explicit template metadata.

Supported render modes:

- `deterministic` — rendered by `ordo.simple` without model assistance.
- `model_assisted` — routed to an AI rendering handoff packet and post-validated deterministically.

A deterministic template must not contain Jinja-style block syntax such as `{% for %}`, `{% if %}`, `loop.index`, `.items()` or complex `default(...)` filters.

A model-assisted template must declare:

```yaml
render_mode: model_assisted
renderer: ai.markdown # or ai.yaml / ai.json
requires_model_rendering: true
validation: strict_confirmed_state_only
tbd_policy: preserve_tbd_until_confirmed
```

The generated handoff packet is not a final artifact. It is an instruction packet for the AI renderer. The rendered result must later pass `validate-artifacts`, `consistency` and `go-no-go`.


## EXECUTION_TRACE IR representation

The source block `execution_trace:` compiles to an IR object with `op: EXECUTION_TRACE.DEF`. Event records compile as ordered immutable event objects. The compiler emits normalized policy only; runtime emits ordered immutable event objects into the persisted trace artifact. Runtime event data MUST NOT be embedded into compiled IR.


### EXECUTION_TRACE.DEF normalized IR fields

`enabled`, `version`, `capture_level`, `storage`, and `replay` are mandatory in normalized IR. The operation configures runtime capture and replay; it is not itself an execution event.
