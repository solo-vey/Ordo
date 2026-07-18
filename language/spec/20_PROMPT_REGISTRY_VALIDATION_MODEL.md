# 20 — Prompt Registry Validation Model

Status: `M65.3 design convention`

## Intent

The prompt registry validation model defines how Ordo/APF packages review prompt files and prompt references before treating them as accepted package contract artifacts.

It complements:

- `prompt_registry` and `prompt_refs` from the Prompt Registry Model;
- `program_level_approval_gate` from the Program-Level Approval Gate Model;
- package manifests and release evidence.

## Validation object

A package MAY define a `prompt_registry_validation_profile` object or equivalent release-gate configuration. The selected profile determines which findings block approval.

Supported profile values are:

- `light`;
- `standard`;
- `strict`.

Supported severity values are:

- `error`;
- `warning`;
- `info`.

Supported decisions are:

- `approved`;
- `approved_with_warnings`;
- `blocked`;
- `not_applicable`.

## Required validation concerns

Prompt registry validation SHOULD cover:

1. registry presence and schema validity;
2. prompt id uniqueness;
3. prompt path existence;
4. required prompt presence;
5. prompt reference resolution;
6. node/artifact/gate attachment target resolution;
7. visibility and language declaration/inheritance;
8. manifest and checksum coverage;
9. quick-start discoverability;
10. authority-safe prompt text review;
11. state-change policy consistency;
12. unused, stale, deprecated, or duplicated prompt warnings.

## Authority boundary

Prompt validation never makes a prompt authoritative over the process. Runtime decisions still belong to nodes, gates, transitions, confirmed state, program contracts, and validation evidence.

## Runtime boundary

M65.3 is not a runtime feature. A future implementation MAY expose these checks through CLI or compiler tooling, but this chapter does not define such command behavior.
