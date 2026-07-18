# M64.2 — Interaction model + process rail + conversation semantics docs

Status: `passed-docs-schema-convention`

M64.2 adds documentation and schema conventions for three package-level behavioral contracts:

```text
interaction_model
process_rail
conversation_semantics
```

## Decision

These constructs are accepted as **source/schema documentation conventions**, not as runtime opcodes and not as mandatory migration for older packages.

```text
Accepted:
  interaction_model docs/schema/value registry
  process_rail docs/schema/value registry
  conversation_semantics docs/schema/value registry
  example source file
  spec chapter 17

Not accepted in M64.2:
  runtime-core changes
  compiler behavior changes
  new opcodes
  deterministic natural-language classifier
  FLOW.JOIN implementation
  SHARED.TAIL.REFERENCE implementation
```

## Why this matters

The M64.1 `program_contract` identifies what a program is and what execution line it targets. M64.2 explains how the live process should behave when a human, AI layer, and CLI/helper layer interact.

## Files added

- `language/INTERACTION_MODEL.md`
- `language/PROCESS_RAIL_SCHEMA_CONVENTION.md`
- `language/CONVERSATION_SEMANTICS.md`
- `language/HYBRID_EXECUTION_POLICY_CONVENTION.md`
- `language/spec/17_INTERACTION_PROCESS_RAIL_CONVERSATION_MODEL.md`
- `language/schemas/interaction_model_schema.yaml`
- `language/schemas/process_rail_schema.yaml`
- `language/schemas/conversation_semantics_schema.yaml`
- `language/registry/INTERACTION_PROCESS_RAIL_CONVERSATION_VALUES.md`
- `language/examples/source/interaction_process_rail_conversation_example.ordo.yaml`

## Validation summary

- YAML examples parse: passed
- YAML schemas parse: passed
- JSON reports parse: passed
- py_compile over CLI/PathWalk/utilities: passed
- Runtime/opcode promotion guard: passed

## Next step

M64.3 should design program-level approval gate lint/profile behavior. It should still avoid runtime-core changes unless a later milestone explicitly promotes these conventions.
