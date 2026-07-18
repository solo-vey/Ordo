# APF rc.8 — Conditional Confirmation Gate Model

## Decision candidate

The new rc.8 confirmation gates should be conditional, not always-on blockers.

## Conditional activation

```yaml
NODE_CHANGE_IMPACT_REVIEW_GATE:
  required_if:
    - nodes_added
    - nodes_removed
    - nodes_reordered
    - node_semantics_changed
    - node_blocking_behavior_changed

GATE_ORDER_CONFIRMATION_GATE:
  required_if:
    - final_tail_changed
    - shared_tail_changed
    - blocking_gate_position_changed

PROCESS_RAIL_CHANGE_CONFIRMATION_GATE:
  required_if:
    - process_rail_changed
    - startup_or_resume_behavior_changed
    - handoff_or_readiness_path_changed

PACKAGE_PROFILE_CHANGE_CONFIRMATION_GATE:
  required_if:
    - package_profile_taxonomy_changed
    - profile_required_checks_changed
    - readiness_status_model_changed
    - deferred_evidence_policy_changed
```

## Not-applicable result

If a gate trigger is false, the gate result should be:

```text
not-applicable
```

not silently omitted.

## Reason

This keeps the APF final tail deterministic while avoiding unnecessary human confirmations when a patch does not affect that surface.
