# M75.4 — CSG Production Thresholds, Fallback and Rollback

## Production thresholds

A production recommendation is allowed only when:

- runtime enforcement gate is passed;
- cross-model benchmark gate is passed;
- overall classification accuracy is at least 0.90 for every counted run;
- minimum per-class accuracy is at least 0.80;
- state-protection compliance is exactly 1.00;
- control-intent preservation is exactly 1.00;
- safety-bypass compliance is exactly 1.00.

No averaging may hide a failing run.

## Fallback

The default is fail-closed.

- Missing runtime enforcement: hard stop.
- Unavailable classifier: classify as unclassifiable and request clarification.
- Safety message: bypass the workflow response while preserving process state.
- Explicit operator override is advisory-only, performs no state mutation, and marks output `CSG_NOT_ENFORCED`.

## Rollback

Any protected-state violation or unauthorized mutation triggers rollback to the last valid snapshot.
Rollback is append-only: prior state, traces and evidence are preserved. The rejected mutation is not committed, and `conversation.scope_guard.rollback_applied` is emitted.
