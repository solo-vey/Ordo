# Chapter 56. Session-trace as a Proof Program

`session-trace` is not a description of the decision tree. It is a record of the actual path taken through a runtime session.

The idea is that every user decision becomes not merely a field in state, but a line in a proof program that can be verified.

## Trace file

The runtime package contains:

```text
runtime/session.ordo.trace
```

At the beginning, the trace is initialized but contains no user decisions. Every accepted `intake --submit` appends a new step.

## Example trace fragment

```ordo-trace
step 001:
  accept N_EVENT_GOAL with answer "Fall of Constantinople" -> N_PATH_SELECT
  evidence sha256:...
  snapshot sha256:...
```

The CLI writes the trace. The model may not create, edit, or “fix” it manually.

## How trace is connected to evidence

After every submit, the CLI updates:

```text
reports/intake_submit_report.json
runtime/evidence/*_evidence.json
runtime/state_snapshots/SESSION-*.json
runtime/session.ordo.trace
runtime/live_session_state.json
```

The evidence report contains trace metadata: path, digest, step, and fragment. This lets the model show proof to the user without directly reading internal compiled targets.

## Why trace does not replace a snapshot

A snapshot shows state. A trace shows the path that led to that state.

```text
snapshot = what is known now
trace = which decisions led here
```

They are therefore verified together.

## Verification

The command:

```bash
cli_embedded/ordo verify-session .
```

checks:

```text
target-set
session-chain
session-trace
canary-scan
```

A clean session must report:

```text
target-set: consistent
session-chain: intact
session-trace: intact
canary-scan: clean
```

If the trace is changed manually, `verify-session` must report failure. If the model bypasses the CLI and creates no trace or evidence, that also becomes visible.

## Why the model needs this

In a long session, a model may forget what was actually confirmed. Trace reduces the risk of that drift:

```text
every step has a node;
every answer has evidence;
every transition has a next node;
every digest can be verified;
the whole session can be logically replayed and verified.
```

Session-trace therefore turns runtime from a mere conversation into a verifiable execution history.
