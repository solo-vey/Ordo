# 030. Result Update Rules

**Version:** `1.0`  
**Backlog:** `BL-BENCH-030`  
**Status:** canonical contract

## 1. Core rule

Benchmark results are immutable observations. Corrections create new events; they never silently rewrite history.

## 2. Update types

### 2.1 New attempt

A rerun receives a new `attempt_id`, even when all other inputs are identical.

### 2.2 Re-evaluation

When only evaluation criteria or evaluator conclusions change, create a new result record referencing the same execution evidence and a new evaluation ID. The new record may supersede the previous evaluation but must not pretend to be a new execution.

### 2.3 Evidence correction

If evidence metadata was wrong, append an `evidence_correction` event with old/new values, reason, authority and checksum. Material changes require re-evaluation.

### 2.4 Invalidation

Use `invalidated` when the attempt cannot support a trustworthy score, for example checksum failure, cross-RUN leakage or fabricated evidence. Preserve the invalid record and reason.

### 2.5 Quarantine

Use `quarantined` for suspected contamination or unresolved comparability. Quarantined records are excluded from standard matrices until resolved.

## 3. Supersession contract

A supersession event must include:

- predecessor record ID;
- successor record ID;
- supersession reason;
- change class: `rerun`, `re_evaluation`, `contract_migration`, `evidence_correction`;
- affected score dimensions;
- authority;
- timestamp;
- whether historical matrices require recalculation.

Only one active successor is allowed per supersession chain and cohort. Branches require explicit conflict resolution rather than silent selection.

## 4. Evaluation contract changes

When scoring rules change:

1. assign a new contract version;
2. do not mutate historical scores;
3. decide whether old evidence is sufficient for re-evaluation;
4. if sufficient, create re-evaluation records;
5. if insufficient, keep the old cohort separate or rerun;
6. rebuild matrices with explicit cohort/version filters.

## 5. Recalculation triggers

Rebuild affected derived views when:

- an active result is added, superseded, invalidated or unquarantined;
- comparability status changes;
- aggregation formula changes;
- evaluation contract migration creates new active scores;
- registry integrity repair changes a referenced record.

## 6. No-op updates

Formatting-only changes to a derived matrix do not create registry events, but do create a new matrix build metadata record if the output artifact changes.

## 7. Audit gates

An update fails if:

- predecessor is missing;
- successor identity is ambiguous;
- reason or authority is absent;
- the old record was overwritten;
- recalculation impact was not evaluated;
- a changed score lacks a new evaluation contract/version binding.
