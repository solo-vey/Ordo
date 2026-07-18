# APF A4 — IR, State and Checkpoint Alignment Policy

## Status

`accepted-package-contract / runtime-enforcement-pending-A6-audit`

## Purpose

This policy aligns APF with the Ordo v0.12 runtime source-of-truth and checkpoint model without changing the approved APF authoring methodology.

## Canonical chain

```text
ordo.yml
→ source/program.ordo.yaml
→ compiled/program.ir.json
→ run_state.json
→ generated_outputs/
```

The editable source is the authoring source of truth. The compiled JSON IR is the machine/runtime contract. Runtime progression is determined from current compiled IR plus validated state. Generated outputs are derivatives and never navigation authority.

## Checkpoint discipline

APF adopts:

```text
one node → one contract → one decision → one checkpoint
```

The earliest incomplete required checkpoint controls the next legal process action. Future information may be retained, but it cannot close an earlier checkpoint or move the process forward.

## State and invalidation

Changing a previously confirmed upstream answer invalidates dependent answers, decisions and generated artifacts. They become `stale`, historical evidence is preserved, and reconfirmation is required before forward movement.

## Output blocking

Artifact generation is blocked while required checkpoint gaps, failed blocking gates, missing confirmations, stale dependencies or IR/state freshness mismatches remain.

## Authority boundary

Prompts, Markdown narrative and chat memory can guide or explain. They cannot determine `next_node`, close checkpoints, mutate confirmed state or authorize output generation.

## Enforcement honesty

A4 establishes the APF package contract and expected validation fields. It does not claim that every rule is already enforced by the current imported runtime package. CLI/runtime capability is verified separately in A6.

## Non-goals

A4 does not:

- add Ordo opcodes;
- alter Ordo compiler/runtime core;
- implement replay, restore or rollback;
- start BL-APF-001 or BL-APF-002;
- change the confirmed APF playbook-authoring flow.
