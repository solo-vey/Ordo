# Shared Validation / Handoff Tail Policy

Version: APF v0.1.0-alpha.19

This policy closes the shared final path used by all Applied Project Factory startup branches. Branches must join this shared tail instead of duplicating validation or handoff logic.

## Flow

```text
source_yaml_generation
→ minimal_validation
→ full_validation_decision
→ validation_result_review
→ correction_loop_if_needed
→ final_unfinished_items_gate
→ handoff_package_generation
→ final_handoff
```

## UX rules

- Source YAML generation requires explicit user approval and a visible scope summary.
- Minimal validation failure shows a short issue list and routes either to correction mode or a blocked/deferred state.
- “Show details” is not a separate branch; details are shown inside correction mode.
- Full validation can be skipped for alpha only as an explicit limitation. Skipped is never passed.
- Correction patches must be scoped and label whether they are technical-only or process-logic changes.
- Final unfinished-items gate blocks active unfinished artifacts/templates until they are completed or removed.
- Handoff is file-first: provide a downloadable package and a concise summary.
- Final handoff offers only two actions: accept package or return to revision.
