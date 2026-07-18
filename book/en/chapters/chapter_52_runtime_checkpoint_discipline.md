# Chapter 52. Runtime Checkpoint Discipline

M57 adds a checkpoint rule to Ordo Runtime Mode.

The idea is simple:

```text
one node at a time
one contract at a time
one decision at a time
earliest incomplete node wins
```

This prevents AI Ordo Developer from compressing several runtime nodes into one response. If business fields, ChangeRecord, trigger/no-op, and naming decisions are all closed at once, it becomes unclear which contract was actually confirmed and where gaps remain.

## Checkpoint table

`run_state` must now contain, or receive from helper commands, a `checkpoint_table`:

```json
{
  "current_node": "",
  "last_closed_node": "",
  "earliest_incomplete_node": "",
  "checkpoint_table": {},
  "forward_allowed": false,
  "open_required_fields": [],
  "node_merge_attempt_detected": false
}
```

## Runtime behavior

If a gap is found, Ordo does not move forward. It returns to the earliest incomplete node, asks one focused question, and continues only after that gap is closed.

`next-step` must prioritize `earliest_incomplete_node`, not the last node the model wanted to reach.

## Why this matters

Checkpoint discipline makes guided intake audit-friendly: at every moment it is visible which node is open, which required fields are confirmed, which remain open, and whether forward movement is allowed.

The book PDF was not regenerated at this step.

## Standard checkpoint-discipline errors

```text
ORDO-CHECKPOINT-001 node advanced before current contract closed
ORDO-CHECKPOINT-002 earlier mandatory node incomplete
ORDO-CHECKPOINT-003 multiple node contracts merged without allow_batch_confirmation
ORDO-CHECKPOINT-004 missing checkpoint table in run_state
ORDO-CHECKPOINT-005 next-step ignored earliest_incomplete_node
ORDO-CHECKPOINT-006 generated output requested while checkpoint gaps remain
```
