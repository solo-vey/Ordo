# Vibe Development Verification Protocol — Incremental Checkpoints

The development loop MUST NOT restart full package verification after every edit.

## Modes

1. **PATCH** — run only checks impacted by changed files relative to the last trusted checkpoint. Unchanged dependency checks may be satisfied by the checkpoint.
2. **CHECKPOINT** — run impacted checks plus a small safety net, then persist a new trusted checkpoint if all selected checks pass.
3. **CANDIDATE** — run **one full PRE_EDITOR** after the implementation batch is complete. This is the only normal development point where the complete PRE_EDITOR suite is required.
4. **RELEASE** — after CANDIDATE passes, perform portable/exact-package verification once before handoff.

Do not run historical regression memories, portable manifests, ZIP build/extract verification, or the complete PRE_EDITOR suite repeatedly between small edits unless a changed file invalidates that specific area or a failure requires it.

## Checkpoint trust

A checkpoint records package input hashes and the PASS status of already verified checks. A check may be reused from the checkpoint only while all files that can affect it remain unchanged. The impact map is explicit and machine-readable in `verification_impact_map.json`.

## Timing

Every incremental run reports elapsed time, selected checks, changed files and budget status. Slow runs are treated as development-process regressions. Current default budgets are PATCH 8 s, CHECKPOINT 20 s, CANDIDATE 60 s and RELEASE 120 s on the local reference environment.

## TDD loop

For a change:

`write failing focused regression → PATCH until GREEN → CHECKPOINT → continue implementation → one CANDIDATE full verification → one RELEASE exact-package verification`.

A full-suite rerun after every intermediate edit is explicitly discouraged.

## Mandatory wall-clock stage timing

Every managed development/release cycle must follow `source/development-timing-policy.json`. Capture the actual `started_at` when each major stage begins. Compute a completed non-final stage duration as the difference between its `started_at` and the next stage `started_at`; for the final stage capture `finished_at` and use `finished_at - started_at`. Candidate shard timing must preserve the plan → shards → aggregate → next/final boundary so the whole shard block is measured independently of per-runner elapsed time. Never fabricate a missing timestamp after the fact.

## FAST vs FULL dependency-aware validation

Validation has two execution classes. **FAST** is used during PATCH/CHECKPOINT authoring loops and selects only checks mapped from changed authoritative inputs, plus unsatisfied transitive dependencies and the small mode safety net. Specific/exclusive impact rules take precedence over generic path rules, and every selection records machine-readable reasons. **FULL** is reserved for explicit CANDIDATE/RELEASE boundaries and runs the complete required verification contour (candidate via persisted shards). A generic source-path match must not drag unrelated historical/heavy checks into a FAST edit loop when a more specific impact rule exists.


## Development / Regression governance (alpha.45)

Every material candidate change follows: protected invariant → pre-change regression evidence → minimal implementation → exact GREEN → directly impacted regressions → candidate evidence. Candidate iteration is targeted; the full accumulated regression/scenario/profile suite remains a RELEASE gate unless explicitly requested earlier. REGRESSION_PROOF and LIVE_PROOF are separate evidence namespaces. Real failures become persistent regression memory. Packaging/context-only changes must prove the declared semantic source surfaces did not change.
