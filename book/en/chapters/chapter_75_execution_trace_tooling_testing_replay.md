# Chapter 75. Validation, Replay, and Practical Use of EXECUTION_TRACE

Once `EXECUTION_TRACE` became a language element and gained runtime semantics, it also had to be tested as strictly as gates, state, and generated outputs.

## What must be tested

The minimum validation set has six layers:

1. canonical YAML examples parse and conform to the closed catalog of values;
2. the compiler creates exactly one `EXECUTION_TRACE.DEF`;
3. the runtime creates an append-only trace, numbers events correctly, and forbids writes after terminal status;
4. integrity validation detects sequence gaps, incorrect `event_count`, and checksum changes;
5. replay modes correctly control re-evaluation and side effects;
6. secrets are redacted before being written to disk.

## How to read a trace

A human reads the trace from top to bottom as an execution chronology. For each event, inspect:

- where it occurred (`location`);
- who performed it (`actor`);
- which data was used (`payload`);
- whether state changed (`state_effect`);
- which gate, decision, or output it is connected to (`correlation`);
- how it ended (`outcome`).

## Four replay modes

`deterministic` repeats preserved inputs and decisions. `re_evaluate` keeps the inputs but recalculates decisions and gates. `simulation` forbids external side effects. `audit_only` executes nothing and only reconstructs the history for inspection.

For analyst-behavior analysis or training, `audit_only` is often sufficient. For regression testing, `deterministic` and `simulation` are usually more useful.

## How trace modification is detected

After the terminal event, the runtime calculates a checksum of the canonical trace representation. If someone changes a payload, sequence, event count, or another part of the history, the recalculated checksum will not match. This is not a digital signature and does not replace protected storage, but it is a reliable control against accidental or unapproved artifact modification.

## What is not included in the trace

`EXECUTION_TRACE` does not store the model's private chain of thought. It stores only an observable decision summary, reason code, evidence references, and factual process transitions. Passwords, tokens, and other secrets must be redacted or replaced with a secure reference before serialization.

## Practical rule

```text
A trace is useful only when it can be verified, stored safely, and replayed under a clearly defined mode.
```
