# DD-ORDO-M65-003 — History Event Factory Prompt Registry Skeleton

Status: accepted  
Milestone: M65.2

## Decision

Implement the M65.1 Prompt Registry adoption plan for `packages/history_event_guided_intake/` as a package-local skeleton patch.

The patch creates prompt files, adds a `prompt_registry` block to `source/program.ordo.yaml`, attaches selected `prompt_refs`, and adds a transitional `PROMPT_MANIFEST.json` with checksums.

## Reason

M65.0 established the model-level Prompt Registry convention, and M65.1 defined the concrete adoption plan. M65.2 turns that plan into reviewable package artifacts without changing runtime core, compiler behavior, CLI commands, or opcodes.

## Constraints

- Helper prompts are supportive guidance only.
- Nodes, gates, state, explicit approval, and CLI/session evidence remain authoritative.
- No compiled IR regeneration is claimed in this milestone.
- No APF branch logic rewrite is included.

## Impact

This improves package discoverability, reviewability, prompt reuse, manifest coverage, and future validation readiness while preserving existing runtime boundaries.
