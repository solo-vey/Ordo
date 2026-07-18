# BL-BENCH-053 — Improvement Plateau and Best Confirmed Version Retention Gate

**Status:** DONE  
**Type:** Process safety / correction-loop governance  
**Priority:** High

## Problem

A document correction or improvement step can repeatedly regenerate a candidate even when the new version provides no measurable quality gain. This creates non-terminating or wasteful loops, may replace a stronger confirmed version with a merely newer version, and can degrade already validated artifacts.

## Objective

Add an enforceable improvement-plateau rule to every document correction and regeneration path. After each attempt, the candidate must be compared with the best currently confirmed version using explicit quality evidence. A new candidate may replace the confirmed version only when measurable improvement is demonstrated.

## Required process behavior

1. Snapshot and bind the best confirmed artifact before regeneration.
2. Record the defect evidence and correction strategy that authorize the attempt.
3. Generate a candidate without overwriting the confirmed artifact.
4. Re-run the applicable validators, semantic checks and cross-artifact gates.
5. Produce a machine-readable delta assessment between candidate and confirmed versions.
6. Accept the candidate only when at least one material improvement is proven and no protected quality dimension regresses.
7. When improvement cannot be proven:
   - reject the candidate;
   - retain the best confirmed version;
   - record `IMPROVEMENT_PLATEAU_REACHED`;
   - terminate the current improvement loop;
   - continue only to the next explicitly allowed process step or terminal decision.
8. Re-entry into the same correction loop requires new defect evidence, new facts, or a materially different correction strategy.

## Measurable improvement signals

At least one of the following must be evidenced:

- a previously failing validator now passes;
- a registered quality defect is closed;
- semantic completeness increases;
- a contradiction is removed;
- missing executable evidence is supplied;
- cross-artifact consistency improves;
- a blocking condition is removed;
- a gate that previously failed now passes.

Editorial variation, rephrasing, formatting-only changes or a newer timestamp are not sufficient.

## Required gates and records

- `G_IMPROVEMENT_DELTA_PROVEN`
- `G_NO_PROTECTED_DIMENSION_REGRESSION`
- `G_BEST_CONFIRMED_VERSION_RETAINED`
- `IMPROVEMENT_ATTEMPT_RECEIPT`
- `IMPROVEMENT_DELTA_REPORT`
- terminal marker `IMPROVEMENT_PLATEAU_REACHED`

The delta report must bind the hashes and versions of the baseline and candidate, applicable criteria, validator outcomes, changed defects, regressions, decision and next route.

## Integration scope

The rule must be integrated into:

- correction and improvement loops;
- document regeneration rules;
- validation-failure handling;
- Driver execution policy;
- terminal eligibility rules;
- multi-cycle improvement mode;
- package self-validation correction passes.

## Prohibitions

The process must not:

- regenerate indefinitely;
- overwrite the confirmed version before acceptance;
- accept a candidate merely because it is newer;
- trade a confirmed quality property for an unrelated cosmetic gain;
- repeat the same correction strategy without new evidence;
- claim improvement without a bound comparison report.

## Acceptance criteria

1. A materially improved candidate replaces the confirmed artifact and preserves the comparison receipt.
2. A formatting-only candidate is rejected and the confirmed artifact remains byte-identical.
3. A candidate that fixes one defect but introduces a protected regression is rejected.
4. Plateau produces `IMPROVEMENT_PLATEAU_REACHED` and exits the loop without another automatic retry.
5. The same strategy cannot retry without new evidence or changed strategy identity.
6. Historical confirmed and rejected candidate versions remain traceable.
7. Decision-tree connectivity and terminal reachability remain valid after integration.

## Source evidence

`backlog_attachments/BL-BENCH-053/SOURCE_PLAYBOOK_EXECUTION_IMPROVEMENT_PLATEAU_RULE.md`


## Implementation closure

Implemented in Alpha 26 through nodes `N092`–`N097`, gates `G_IMPROVEMENT_DELTA_PROVEN`, `G_NO_PROTECTED_DIMENSION_REGRESSION`, and `G_BEST_CONFIRMED_VERSION_RETAINED`, plus terminal `T_IMPROVEMENT_PLATEAU_REACHED`. The runtime preserves the baseline until acceptance, emits bound attempt and delta records, rejects non-material or regressive candidates, and blocks same-strategy retry without new evidence.
