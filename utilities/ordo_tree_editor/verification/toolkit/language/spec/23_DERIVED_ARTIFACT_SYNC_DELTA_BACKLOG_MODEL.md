# 23. Derived Artifact Sync, Delta Backlog, and Prompt Packaging Checks

Status: M67.0 accepted model chapter.

## Model boundary

This chapter defines a package-consistency layer. It does not define runtime execution, compiler regeneration, CLI implementation, new opcodes, or automatic rebuilds.

## Source-of-truth first

Packages must make clear which files are authoritative. Derived artifacts may summarize or render source, but they do not override source unless an explicit package contract says so.

## Derived artifact declaration

A declaration answers: artifact identity, location, source, derivation method, freshness policy, and stale action.

## Delta backlog

Delta backlog entries prevent silent drift. A package can proceed with warnings only when deferred sync work is explicit and traceable.

## Prompt registry packaging checks

Standard profile checks prompt registry shape, prompt path existence, prompt ref resolution, manifest coverage/checksums, startup profile linkage, and authority boundary safety.

## Relationship to M64-M66

M64 provides program-level contract conventions. M65 provides prompt registry conventions. M66 provides startup package profile conventions. M67 ties these into package consistency review.

## Decision model

```text
if any error:
  decision = blocked
elif any warning:
  decision = approved_with_warnings
else:
  decision = approved
```

## Non-change statement

M67.0 introduces no runtime-core changes, no compiler behavior changes, no CLI command changes, no Semantic JSON IR execution changes, and no new opcodes.
