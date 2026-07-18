# A4 — IR, State and Checkpoint Alignment Report

## Result

A4 aligned the APF working baseline with the Ordo v0.12 source → IR → state → output and runtime checkpoint conventions.

## Added contracts

- `docs/APF_RUNTIME_SOURCE_OF_TRUTH_CHAIN.yaml`
- `docs/APF_RUN_STATE_CONTRACT.yaml`
- `docs/APF_RUNTIME_CHECKPOINT_CONTRACT.yaml`
- `docs/APF_A4_IR_STATE_CHECKPOINT_ALIGNMENT_POLICY.md`

## Adopted rules

- compiled JSON IR is the runtime machine contract;
- editable YAML remains the editable authoring source;
- current compiled IR plus validated state determine legal progression;
- `earliest_incomplete_node` controls the next required action;
- generated outputs are blocked while checkpoint gaps remain;
- upstream change invalidates dependent state and artifacts;
- prompts and Markdown cannot own navigation or state mutation.

## Enforcement classification

| Capability | A4 status |
|---|---|
| Source/IR/state/output chain | accepted APF contract |
| Checkpoint table fields | accepted APF contract |
| Earliest incomplete node | accepted APF contract |
| Forward blocking | accepted APF contract |
| Stale dependency invalidation | accepted APF contract |
| CLI/runtime enforcement | pending A6 capability audit |
| Replay/snapshot/diff/restore | not claimed; pending A6 |

## Scope protection

No APF authoring-flow node, confirmed rc.12 policy, Ordo core file or deferred backlog item was changed or activated.
