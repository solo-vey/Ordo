# Safe Correction and Selective Replay

`correction_contract` is an opt-in, fail-closed contract for correcting an
upstream state value without silently discarding unrelated confirmed state.
Each permitted source field explicitly declares the downstream state,
derivations, gates, tests, and artifacts made stale by that correction, plus
the affected gates that must be replayed.

```yaml
correction_contract:
  version: "1.0"
  mode: strict
  rules:
    - source: customer_name
      invalidate:
        state: [customer_summary]
        derivations: [N_DERIVE_SUMMARY]
        gates: [G_SUMMARY_READY]
        tests: [TC_SUMMARY]
        artifacts: [A_CUSTOMER_REPORT]
      replay:
        gates: [G_SUMMARY_READY]
```

Validate a declaration:

```text
ordo validate-correction-contract PACKAGE_PATH
```

Create a reviewable correction plan without changing the input snapshot:

```text
ordo plan-correction PACKAGE_PATH --state runtime/state.json --path customer_name --value '"Updated customer"' --corrected-state reports/corrected_state.json
```

The plan clears only declared downstream state paths in the *new* corrected
copy, lists stale non-state dependencies, replays only declared gates, and
records the preserved state paths. It never mutates the supplied state file or
executes model calls, tests, or artifact generation.
