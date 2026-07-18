# DD-ORDO-M66-001 — Package Startup Standard

## Status

Accepted as M66.0 documentation/schema convention.

## Context

M64 introduced program-level contracts and approval-gate conventions. M65 introduced prompt registry and prompt validation conventions.

After those additions, packages can now declare who they are, how they should be interacted with, how helper prompts are attached, and how prompt references should be validated. The remaining gap is package startup: which file or prompt should be used first, for which audience, and under which readiness conditions.

## Decision

Add `startup_package_profile` as a top-level package/source convention.

It defines:

- startup modes;
- entry files;
- default startup path;
- audience/visibility;
- readiness gates;
- authority boundary.

## Non-decision

This does not add runtime behavior, CLI commands, compiler behavior, opcodes, or deterministic startup-intent classification.

## Consequences

Packages can distinguish quick-start prompts, runtime start prompts, developer start prompts, and CLI/operator startup instructions without relying on ad-hoc naming alone.

Startup can be linted and reviewed independently from runtime execution.
