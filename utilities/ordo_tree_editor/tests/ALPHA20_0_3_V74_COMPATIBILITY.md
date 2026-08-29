# alpha.20.0.3 ↔ Compiler V7.4 compatibility

Validated against Risk Factor Passport alpha 0.8.7.

- V7.4 graph verification: 71/71 reachable.
- Execution dispatch verification: PASS for all 71 elements.
- `N_TRIGGER_SOURCE_BLOCK` is phase-aware: model execution on `respond` only.
- `ARTIFACT.PRESENT_FOR_REVIEW` uses an explicit runtime executor.
- Legacy semantic `state_updates` are converted into StatePatch during retry and preserved.
- Recent history is included for semantic calls without opt-in markers.
- Runtime graph mechanics (`on_pass`, `on_fail`, routes/branches, dynamic route metadata) are stripped from semantic task context.
- Semantic state context uses a larger bounded budget and records explicit truncation metadata; a model gate may not PASS on incomplete context.
- GateFailure evidence and gate transitions are visible in the Run transcript.

Known source-playbook issue retained intentionally: alpha 0.8.7 has 28 declared inputs absent from canonical state schema. V7.4 reports these as semantic compilation issues; they are not silently suppressed.
