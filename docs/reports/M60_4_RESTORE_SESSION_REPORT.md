# M60.4 Restore Session Report

M60.4 adds native append-only restore/backtrack support to the Ordo runtime CLI.

## New command

```bash
ordo restore-session <package> --to-seq <N> [--reason "..."]
```

## Contract

Restore is not destructive rollback. It copies state from an existing session snapshot and appends a new runtime event:

```text
reports/restore_session_report.json
runtime/evidence/*RESTORE_TO_SEQ_<N>*_evidence.json
runtime/state_snapshots/SESSION-*_RESTORE_TO_SEQ_<N>.json
runtime/session.ordo.trace step action=restore_session
runtime/live_session_state.json
```

## Validation

`verify-session` validates restore through the existing session-chain, target-set, session-trace, evidence digest, snapshot hash, and canary checks.

## Scope exclusions

This milestone does not modify PathWalk code, does not calibrate PathWalk score weights, and does not introduce Python/Java compilation targets.
