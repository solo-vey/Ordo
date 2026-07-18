# APF v0.1.0-alpha.20 — Whole-Tree Integration Review

Status: human review closed; structural scan recorded in `APF_V0_1_0_ALPHA_20_VALIDATION_REPORT.json`.

## Reviewed blocks

1. Startup branches integration
2. Shared output/template joins
3. Shared validation/handoff joins
4. Terminal/deferred/unfinished gates
5. Orphans/dead-ends/duplication
6. Closure decision

## Confirmed architecture

```text
START
→ startup mode selection
  → branch 1: domain model + decision tree
  → branch 2: manual decision tree entry adapter
  → branch 3: free dialogue
  → branch 4: existing process improvement
→ shared output/template subflow where terminal outputs are involved
→ source YAML approval/generation
→ shared validation/handoff tail
```

## Integration rules

- Branch 2 is an entry adapter and must not duplicate branch 1 review logic.
- Branch 3 free-dialogue extraction must preserve output/template mentions and then join the standard draft-tree review path.
- Branch 4 corrections are scoped and then join the shared validation/handoff tail.
- Terminal points require output policy.
- Document-like artifact review is file-first.
- Unfinished active templates/artifacts block use until completed or removed.
- Removed artifacts are excluded from active terminal binding.
- Full validation skipped for alpha is a limitation, not passed.
- Validation/handoff tail is shared and not duplicated inside branches.

## Legacy compatibility nodes

Alpha.20 keeps several older nodes for compatibility/history but marks them as `deprecated_legacy_compatibility`. They are not active runtime orphans.
