# M71.4 — Runtime Application Order and Trace Evidence Validation

Status: `implemented-package-runtime-contract / passed-validation`

## Scope

M71.4 validates how stable semantic prompt references are applied after an executable runtime step has already been selected, and defines the evidence payload that can be recorded by a runtime/session-trace surface.

## Accepted order

1. CLI / canonical JSON IR selects the current node, gate, or artifact.
2. Only that executable object's `prompt_refs` are collected.
3. `use` is validated against the controlled phase vocabulary.
4. Source-list order is preserved for deterministic application.
5. Each `prompt_id` resolves through `PROMPT_MANIFEST.json`.
6. File existence and SHA-256 are verified.
7. Prompt guidance is applied locally before the action represented by `use`.
8. User-visible output does not reveal prompt text.
9. Recordable evidence stores identity, phase, checksum, and ordinal only.

## Evidence contract

Required fields:

- `prompt_id`
- `use`
- `sha256`
- `ordinal`

Forbidden in the prompt application record:

- prompt body/text;
- hidden reasoning;
- prompt-derived `next_node`;
- gate/approval/state authority.

## Boundary

This milestone does not add a new opcode and does not change the core or embedded session-trace writer. It makes the package/runtime evidence contract explicit and testable. Existing CLI/JSON IR remains the sole navigation and state authority.

## Validation

- M71.2–M71.4 focused tests: 17 passed.
- package clean-check standard: passed.
- checks: 43; warnings: 0; errors: 0.
- all refs resolve to manifest entries and valid checksums.
- controlled phases validated.
- source-list order validated.
- trace schema forbids prompt text and navigation fields.
- prompt authority safety heuristic passed.

## Untouched

- business transitions;
- state schema and confirmed-event logic;
- gates and approvals;
- compiler and opcodes;
- core/embedded CLI session-trace implementation;
- compiled IR.
