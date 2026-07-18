# 33. EXECUTION_TRACE Core Language Model

## Status

`EXECUTION_TRACE` is a first-class Ordo core runtime artifact. It records the observable history of one process run as an append-only, ordered event stream.

## Purpose

The element provides a canonical source for replay, audit, debugging, regression comparison, process improvement and analyst-training review. It records what the program executed, not private model chain-of-thought.

## Canonical declaration

```yaml
execution_trace:
  id: trace.history_event.001
  version: "1.0"
  run:
    run_id: run.history_event.001
    process_id: history_event.guided_intake
    process_version: "1.42"
    execution_mode: normal
    runtime_mode: chat_internal
    trace_source: hybrid
  status: running
  started_at: "2026-07-10T14:00:00+03:00"
  actor:
    actor_type: analyst
  source:
    entry_point: start
    input_refs: []
  capture_level: standard
  events: []
  replay:
    replayable: false
    replay_mode: deterministic
    required_inputs_preserved: false
  integrity:
    event_count: 0
    sequence_complete: true
```

## Language identity

- element kind: `core_runtime_artifact`
- canonical source key: `execution_trace`
- canonical IR op: `EXECUTION_TRACE.DEF`
- cardinality: one primary trace per `RUN`; child/sub-run traces may reference a parent run
- storage semantics: append-only event stream plus references to snapshots, diffs, decisions, gates and artifacts
- default capture level: `standard`
- default replay mode: `deterministic`

## Trace event contract

Every event has a monotonically increasing `sequence`, stable `event_id`, closed-catalog `event_type`, timestamp, actor, payload and outcome. Optional location, state effect and correlation blocks connect the event to `NODE`, `PATH`, `GATE`, `DECISION`, `STATE`, `OUTPUT` and parent events.

## Capture levels

- `minimal`: run lifecycle, selected path, gates and outputs.
- `standard`: minimal plus user inputs, decisions and state diffs.
- `full`: standard plus actions, validations, warnings and checkpoints.
- `audit`: full plus actor attribution, integrity chain and evidence references.

## Replay modes

- `deterministic`: preserve recorded answers and decisions.
- `re_evaluate`: preserve inputs but recompute gates and decisions.
- `simulation`: replay without external side effects.
- `audit_only`: read and inspect without execution.

`replay.replayable: true` is valid only when all required inputs are preserved or securely referenced and external dependencies have an explicit replay strategy.

## Security and privacy

The trace MUST NOT contain passwords, tokens, secrets, unrestricted confidential documents or private model chain-of-thought. Sensitive values use redaction, secure references or hashes. Model decisions use a concise decision summary, reason code and evidence references.

## Core invariants

1. Event sequence is unique and strictly increasing.
2. Recorded events are immutable; corrections append a new event.
3. `integrity.event_count` equals the actual event count.
4. Completed, failed and cancelled traces contain a terminal run event.
5. Every evaluated gate has a correlated gate event.
6. Every generated output has an `artifact_generated` event.
7. State references must resolve when replayability is claimed.
8. The trace records the exact process and version that executed.
9. Side effects are explicitly identified.
10. `trace_source` continues to distinguish model self-report, runtime evidence and hybrid traces.

## Compatibility

The older top-level `trace:` structure remains a legacy compatibility view. New programs and generated IR MUST use `execution_trace:` and `EXECUTION_TRACE.DEF`. Compatibility adapters may map legacy fields such as `selected_path`, `decision_log`, `state_snapshots` and `gate_report` into canonical trace events.
