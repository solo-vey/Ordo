# APF Program-level Contract Alignment Policy

## Status

- milestone: `A1`
- alignment target: `Ordo v0.12`
- schema profile: `program_level_contract_v1`
- APF baseline source: `v0.1.0-rc.12-confirmed-closure`
- implementation status: `applied-working-state`

## Purpose

This policy makes the APF top-level execution contract explicit without changing the accepted APF authoring logic.
It aligns APF metadata with the Ordo v0.12 program-level contract convention.

## Canonical contract

The machine-readable source for this milestone is:

```text
docs/APF_PROGRAM_LEVEL_CONTRACT.yaml
```

## Interpretation rules

1. The contract is a source/schema convention, not a new opcode.
2. APF does not claim runtime enforcement that is not supplied by the parent Ordo package.
3. `chat_internal` is used for the current APF baseline because APF is presently operated as a disciplined AI-guided authoring process; full runtime packaging is not claimed in A1.
4. `standard_applied_module` identifies APF as a reusable applied module.
5. Human authority remains final for content decisions, approval points, and release confirmation.
6. AI drives the guided authoring process but may not silently mutate confirmed process contracts.
7. CLI and helper utilities provide deterministic validation only within their verified capability.
8. APF-local validation commands must not be misrepresented as parent Ordo core commands.

## Required review points

The A1 contract names review points for the entire adaptation line. Naming a future review point does not start that milestone.

- `approve_program_contract` — completed by the user's instruction to perform A1 and this applied alignment.
- `approve_runtime_profile` — covered at metadata level in A1; detailed interaction semantics remain A2.
- `approve_process_rail_contract` — reserved for A2.
- `approve_prompt_registry_migration` — reserved for A3.
- `approve_validation_profile` — reserved for A5.
- `approve_final_package` — reserved for A7.

## Non-goals

A1 does not:

- modify APF decision-tree or authoring flow;
- add process-rail or conversation-semantics behavior;
- introduce Prompt Registry artifacts;
- change Semantic JSON IR;
- add opcodes;
- start `BL-APF-001` or `BL-APF-002`;
- modify Ordo language or runtime core.

## Validation expectation

A1 passes when:

- canonical program contract exists;
- required identities and compatibility target are explicit;
- runtime responsibility split is declared;
- review points and validation commands are listed;
- enforcement status is honest;
- existing APF scope and confirmed rc.12 behavior remain unchanged.
