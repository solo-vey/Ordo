# Deterministic Replay and Evidence Export

Ordo records runtime events in `runtime/execution_trace.json`.  Each event has a
normalized `replay_record`: node and phase, analyst input, selected route,
state references, checkpoint/decision identifiers, and an evidence class.
The record contains a bounded auditable decision summary, never hidden model
reasoning.

## Replay a run

Run replay from a clean Git checkout.  The package must be inside that checkout.
No model call or live external dependency is performed during deterministic
replay.  A trace that requires an unrecorded dependency is reported as
`blocked`, rather than guessed or executed.

```bash
ordo replay \
  --checkout /path/to/clean/Ordo \
  --package /path/to/clean/Ordo/example-package \
  --trace /path/to/run/runtime/execution_trace.json
```

The command creates `reports/deterministic_replay_report.json` and a matching
Markdown report.  It returns zero only when the checkout is clean, the trace
integrity is valid, the package source hash matches the trace, and all required
inputs/dependencies are replayable.

## Export evidence without modifying state

```bash
ordo export-replay-evidence \
  --trace /path/to/run/runtime/execution_trace.json \
  --state /path/to/run/runtime/state_snapshots/RUN_state_final.json \
  --out /path/to/evidence-export
```

The export copies only replay evidence and writes JSON and Markdown reports.
It hashes the supplied state before and after export; any mutation makes the
report fail.
