# EXECUTION_TRACE Runtime & Compiler Contract — M72.2

Status: accepted / implemented

## Compiler contract

`execution_trace:` compiles to one `EXECUTION_TRACE.DEF`. Defaults are normalized during compilation. Invalid capture/replay values fail compilation. The IR contains policy only.

## Runtime contract

One enabled definition produces one append-only `ordo-execution-trace.v1` JSON artifact per run. Runtime initializes it before the first executable step, appends filtered events, redacts sensitive fields, calculates integrity metadata, records a terminal event, and rejects further appends.

## Capture policy

- minimal: run/path/gate/output/error;
- standard: minimal plus input/decision/state/approval;
- full: standard plus action/template/checkpoint/warning;
- audit: all registered events.

All levels use the same schema.

## Replay policy

- deterministic: preserve recorded choices;
- re_evaluate: preserve inputs, recalculate logic;
- simulation: no external side effects;
- audit_only: no execution.

Replay readiness requires valid integrity, preserved required inputs when replayable, and a supported replay mode.

## Persistence and security

Default: `runtime/execution_trace.json`. Sensitive key names are redacted before persistence. Model chain-of-thought is never recorded; only structured decision summaries, reason codes, and evidence references are allowed.
