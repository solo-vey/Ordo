# M64.1 — Program-level Contract Schema Convention Report

Status: `passed-schema-convention`

## Scope

M64.1 implements the first M64 first-wave design/spec patch. It introduces a documented `program_contract` source-level convention and supporting schema/value documentation.

## Added

- `language/PROGRAM_LEVEL_CONTRACT.md`
- `language/spec/16_PROGRAM_LEVEL_CONTRACT_MODEL.md`
- `language/schemas/program_level_contract_schema.yaml`
- `language/registry/PROGRAM_LEVEL_CONTRACT_VALUES.md`
- `language/examples/source/program_level_contract_example.ordo.yaml`
- `docs/program_level_contract.md`

## Decision

`program_contract` is accepted as a schema/package authoring convention, not as a new opcode or IR object.

## Explicit non-changes

- Runtime core unchanged.
- Compiler behavior unchanged.
- CLI command set unchanged.
- Semantic JSON IR execution behavior unchanged.
- No new opcodes added.
- `FLOW.JOIN` not implemented.
- `SHARED.TAIL.REFERENCE` not implemented.
- Conversation semantics not promoted to deterministic natural-language classifier.

## Next step

`M64.2 — Interaction model + process rail + conversation semantics docs`.
