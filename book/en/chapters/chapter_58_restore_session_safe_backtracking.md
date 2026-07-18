# Chapter 58. Restore-session: Safe Backtracking

Sometimes, during guided intake, the user wants to change a previous answer:

```text
Let's return to the previous step.
I want to choose a different path.
No, that answer was wrong.
```

Before M60.4, the Ordo runtime had no native command for this kind of return. That created a temptation for external utilities or the model itself to edit session state manually. This is dangerous because it can hide the fact that history was changed.

M60.4 adds:

```bash
ordo restore-session <package> --to-seq <N>
```

Inside a runtime package:

```bash
./cli_embedded/ordo restore-session . --to-seq <N>
```

## Restore does not delete history

The main rule is:

```text
restore-session does not erase earlier snapshots.
restore-session appends a new event to history.
```

Ordo does not rewind the session as if later steps had never happened. The CLI takes state from an earlier snapshot and creates a new restore event.

This matters for trust: both a human and a verification utility can see that a return occurred.

## What restore-session writes

A successful restore creates or updates:

```text
reports/restore_session_report.json
runtime/evidence/*RESTORE_TO_SEQ_<N>*_evidence.json
runtime/state_snapshots/SESSION-*_RESTORE_TO_SEQ_<N>.json
runtime/session.ordo.trace
runtime/live_session_state.json
```

The trace receives a step such as:

```text
action: restore_session
node: RESTORE_TO_SEQ_<N>
```

Backtracking is therefore part of the evidence history, not a hidden file operation.

## How the model must behave after restore

After restore, the model must not decide on its own which question comes next. It must call the CLI again:

```bash
./cli_embedded/ordo next-step . --format auto
```

Only then may it ask the next question.

## How to verify restore

The final verification remains:

```bash
./cli_embedded/ordo verify-session .
```

A session is healthy only if the restore event preserves:

```text
target-set
session-chain
session-trace
evidence digest
snapshot hash
canary scan
```

## Why this matters for PathWalk

Scenario-testing utilities such as PathWalk often contain correction and backtrack scenarios. After M60.4, PathWalk must not rewrite runtime state itself. It must call the embedded CLI `restore-session`.

This preserves the central property of the Ordo runtime: every important transition is visible in evidence artifacts.

## M60.4 formula

```text
JSON IR decides.
Ordo-code explains.
Session-trace proves.
Restore-session goes back without erasing history.
```
