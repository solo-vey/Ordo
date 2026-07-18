# Contractual Manual Run Journey Capture

Ordo runtime records every manual intake interaction in two synchronized artifacts:

- `runtime/manual_run_journey.events.jsonl`: append-only audit source with a digest chain.
- `runtime/MANUAL_RUN_JOURNEY.yaml`: atomic consolidated human- and machine-readable view.

The runtime records accepted and rejected answers at interaction time, state digests and diffs, transitions, trace and snapshot evidence. Rejected answers must not mutate canonical state. The journey remains valid for incomplete, blocked, interrupted, failed, and completed runs.

Validate with:

```bash
ordo validate-journey <package>
```

Replay, cross-version migration, automatic output comparison, and branch replay are explicitly outside this version.
