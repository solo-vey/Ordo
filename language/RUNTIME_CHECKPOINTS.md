# Runtime Checkpoint Discipline

M57 adds Runtime Checkpoint Discipline to Ordo Runtime Mode.

Core rule:

```text
one node at a time
one contract at a time
one decision at a time
earliest incomplete node wins
no forward movement while earlier mandatory contracts are incomplete
```

## Node closure status

Each runtime node has one of these closure states:

```text
open
incomplete
closed
blocked
not_applicable
```

`closed` means all required fields owned by the node are confirmed/present in run state. `incomplete` means the node has partial data but still has required gaps. `open` means the node has not been answered. `blocked` means a helper/gate prevents progress. `not_applicable` means the node has no required checkpoint fields for the selected path.

## Run state checkpoint table

Runtime helpers enrich `run_state` with:

```json
{
  "current_node": "",
  "last_closed_node": "",
  "earliest_incomplete_node": "",
  "checkpoint_table": {
    "N1_PATH_SELECTION": {
      "status": "closed",
      "required_fields": [],
      "confirmed_fields": [],
      "open_gaps": [],
      "next_allowed": ""
    }
  },
  "forward_allowed": false,
  "open_required_fields": [],
  "node_merge_attempt_detected": false
}
```

## Gap handling rule

If a gap is discovered:

1. stop forward progress;
2. identify `earliest_incomplete_node`;
3. return to that node;
4. ask exactly one focused question;
5. continue only after the gap is closed.

## Node merge rule

Runtime nodes must not be merged in one assistant step unless the package explicitly declares:

```yaml
allow_batch_confirmation: true
```

Without that flag, a runtime assistant may summarize context, but it must close one node/contract at a time.

## Output rule

`generate-output` is blocked if checkpoint gaps remain. This is reported with `ORDO-CHECKPOINT-006`.
