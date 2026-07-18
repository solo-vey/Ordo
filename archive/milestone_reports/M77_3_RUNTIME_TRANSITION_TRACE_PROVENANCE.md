# M77.3 — Runtime Transition, Trace, and Provenance Semantics

## Status

Implemented.

## Runtime semantics

- `FLOW.JOIN` executes only from one declared incoming branch.
- The runtime does not wait for every possible branch; it follows the actual path.
- State is checked against the authored `state_contract` and merged fail-closed.
- Branch-local fields do not cross the join boundary.
- Protected-field conflicts are never resolved implicitly.
- The join target is entered only after required fields and merge rules pass.

## Shared-tail semantics

- Entry projects caller state through `import_state.allow` and `rename`.
- Required imports are checked before entering the tail.
- Caller-only fields remain outside the tail sandbox.
- Exit projects only `export_state.allow` fields back to the caller.
- Protected caller fields cannot be overwritten by tail output.
- The caller path history and source declaration provenance are retained across entry and return.

## Trace events

Join transitions emit:

- `flow_join_entered`
- `flow_join_state_merged`
- `flow_join_exited`

Shared-tail transitions emit:

- `shared_tail_reference_resolved`
- `shared_tail_entered`
- `shared_tail_exited`
- `shared_tail_returned`

The trace is descriptive evidence. It never authorizes a transition that failed state-contract validation.
