# APF rc.7 → rc.8 Handoff

## Current baseline

```text
baseline: APF_TRANSFER_PACKAGE_CURRENT_STATE_RC7_CLOSURE.zip
status: accepted-baseline
```

## Recommended next APF patch

```text
APF rc.8 — Playbook authoring confirmation and node-change review gate
```

## Why rc.8 is next

rc.7 introduced explicit gate wiring and external evidence contracts. The next APF risk is silent process drift: a patch may add, move, or change process nodes/gates/settings without a human-readable confirmation list.

## Proposed rc.8 scope

```text
NODE_CHANGE_IMPACT_REVIEW_GATE
PROCESS_RAIL_CHANGE_CONFIRMATION_GATE
GATE_ORDER_CONFIRMATION_GATE
PACKAGE_PROFILE_CHANGE_CONFIRMATION_GATE
HUMAN_CONFIRMATION_REGISTER
```

## Expected rc.8 behavior

When APF changes graph nodes, gate ordering, package profile logic, startup behavior, or readiness settings, APF must produce a confirmation list before final ready/go.

Minimum confirmation fields:

```text
change_id
affected_node_or_gate
change_type: added | moved | renamed | split | merged | removed | severity_changed | setting_changed
old_position
new_position
reason
impact
requires_user_confirmation
confirmation_status
```

## Out of scope for rc.8

```text
- Ordo language package changes
- CLI command implementation
- compiler/runtime changes
- FLOW.JOIN / SHARED.TAIL adoption
```
