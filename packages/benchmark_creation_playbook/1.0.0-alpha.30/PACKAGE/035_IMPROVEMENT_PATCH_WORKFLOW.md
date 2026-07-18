# 035 — Improvement Patch Workflow

## Status

Canonical contract for `BL-BENCH-035`.

## Purpose

Convert a confirmed or probable diagnostic finding into a bounded, versioned and reversible improvement without rewriting unrelated benchmark assets.

## Entry criteria

An improvement patch may start only when:

1. a diagnostic case exists;
2. root-cause confidence is `confirmed` or `probable`;
3. the target component is identified;
4. baseline package, result cohort and evaluation contracts are frozen;
5. patch scope and regression scope are approved.

Unsupported or merely plausible hypotheses may create backlog items, but may not mutate the benchmark baseline.

## Patch identity

Every patch receives an immutable `patch_id` and records:

- source diagnostic case;
- primary and contributing root causes;
- target component and version;
- exact files, sections, nodes or rules allowed to change;
- expected behavioral effect;
- prohibited side effects;
- rollback source;
- selected regression scenarios;
- acceptance and stop criteria.

## Workflow

1. Freeze the current baseline and checksums.
2. Create a patch proposal.
3. Define an explicit change allowlist.
4. Apply the minimum sufficient change.
5. Produce structural and semantic diffs.
6. Reject unexplained out-of-scope changes.
7. Rebuild only derived artifacts whose lineage requires regeneration.
8. Run targeted regression scenarios.
9. Run invariant and contamination checks.
10. Compare against the frozen baseline.
11. Accept, reject or roll back the patch.
12. Register the new package version and supersession relation.

## Required evidence

- `IMPROVEMENT_PATCH_RECORD.json`;
- before/after checksums;
- structural and semantic diff;
- regression selection record;
- regression results;
- acceptance or rollback decision;
- updated lineage manifest.

## Guardrails

- A patch must not silently change RUN semantics, scoring contracts, Driver behavior and package content in one undifferentiated mutation.
- Benchmark data must never be edited merely to make a package look better.
- Historical results remain immutable.
- Failed patches remain auditable.
- A patch that changes an evaluation contract creates a new comparison cohort.

## Terminal dispositions

- `PATCH_ACCEPTED`;
- `PATCH_REJECTED`;
- `PATCH_ROLLED_BACK`;
- `PATCH_BLOCKED_EVIDENCE`.

## Completion evidence

This contract, the patch record template and the cumulative Ordo nodes complete `BL-BENCH-035`.
