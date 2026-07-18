# APF rc.8 — Process Rail Change Confirmation Policy

## Purpose

`PROCESS_RAIL_CHANGE_CONFIRMATION_GATE` checks changes that affect the overall APF process rail, not just one node.

## Gate ID

```text
Node ID: N_SHARED_TAIL_PROCESS_RAIL_CHANGE_CONFIRMATION_GATE
Gate name: PROCESS_RAIL_CHANGE_CONFIRMATION_GATE
```

## Trigger

Run when a patch changes:

```text
- canonical playbook authoring lifecycle
- shared tail
- analyst intake path
- startup / resume behavior
- final handoff path
- readiness decision path
- conditional activation model
```

## Required comparison

```text
old process rail
new process rail
changed segments
reason for change
risk / impact
confirmation status
```

## Confirmation requirement

If the changed rail affects how a future playbook/package is created or validated, it requires explicit human confirmation before `ready/go`.
