# Chapter 74. EXECUTION_TRACE — the Complete History of Process Execution

`EXECUTION_TRACE` is a first-class Ordo language element that preserves the factual history of one process run. It is not an ordinary log and not hidden model reasoning. It is a structured, verifiable record of which nodes, paths, actions, decisions, gates, state changes, and outputs actually occurred during execution.

The main rule is:

```text
one RUN → one primary EXECUTION_TRACE
```

The trace is stored as an append-only sequence of events. An event already recorded is not rewritten; a correction or clarification is added as a new event. This allows the trace to support audit, debug, replay, regression testing, analyst-behavior analysis, and playbook improvement.

## Main structure

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

## What one event records

Each event has a sequence number, stable ID, type, time, actor, payload, and outcome. When needed, it also references the active node/path/phase, state before and after, a decision, gate, output, or parent event.

## Detail levels

- `minimal` — run lifecycle, path, gates, and outputs;
- `standard` — also inputs, decisions, and state diffs;
- `full` — also actions, validations, warnings, and checkpoints;
- `audit` — full evidentiary detail, actor attribution, and integrity chain.

The default is `standard`.

## Replay

A trace can support four modes: `deterministic`, `re_evaluate`, `simulation`, and `audit_only`. `replayable: true` is allowed only when required inputs are preserved or safely referenced and a strategy is defined for external dependencies.

## Security

The trace does not store passwords, tokens, secrets, complete confidential documents, or private chain of thought. Sensitive values use redaction, secure references, or hashes. Model decisions retain a short reason code and evidence references.

## Difference from TRACE.LOG

`TRACE.LOG` is an individual diagnostic message. `EXECUTION_TRACE` is the complete canonical artifact for an entire run. Many `TRACE.LOG` events may be part of one `EXECUTION_TRACE`, but they do not replace it.

## Legacy compatibility

The old `trace:` block remains a compatible representation. New Ordo programs should use `execution_trace:`. Legacy fields are converted by an adapter into canonical trace events.

## How the compiler and runtime work with EXECUTION_TRACE

The compiler does not write execution history. It transforms the `execution_trace:` block into a normalized `EXECUTION_TRACE.DEF` instruction: whether tracing is enabled, which detail level to use, where to write the file, and which replay mode is allowed.

Before the first step, the runtime creates `runtime/execution_trace.json`. After every meaningful action, it appends an immutable event. At completion, it adds a terminal event, final state, and checksum. After terminal status, new events are forbidden.

The `minimal` level stores only the traversal skeleton; `standard` adds answers, decisions, and state changes; `full` adds technical actions and warnings; `audit` includes all permitted event types. The file format remains the same in every case.

Replay can be deterministic, re-evaluate rules, simulate without side effects, or be audit-only. Secrets are automatically redacted, and the model's internal chain of thought never enters the trace.
