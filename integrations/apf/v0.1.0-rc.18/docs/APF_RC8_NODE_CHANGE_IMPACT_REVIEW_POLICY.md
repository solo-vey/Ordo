# APF rc.8 — Node Change Impact Review Policy

## Purpose

`NODE_CHANGE_IMPACT_REVIEW_GATE` checks whether APF changed process graph nodes in a way that affects playbook/package creation.

## Gate ID

```text
Node ID: N_SHARED_TAIL_NODE_CHANGE_IMPACT_REVIEW_GATE
Gate name: NODE_CHANGE_IMPACT_REVIEW_GATE
```

## Trigger

Run this gate when any of the following are true:

```text
nodes_added: true
nodes_removed: true
nodes_renamed: true
nodes_reordered: true
node_semantics_changed: true
node_blocking_behavior_changed: true
node_aggregator_behavior_changed: true
```

## Checks

The gate must list:

```text
- added nodes
- removed nodes
- renamed nodes
- moved nodes
- nodes whose blocking behavior changed
- nodes that became aggregator-only
- nodes whose semantic meaning changed
- affected graph/rendering/readiness paths
```

## Result model

```json
{
  "gate": "NODE_CHANGE_IMPACT_REVIEW_GATE",
  "status": "passed | needs-human-confirmation | blocked | not-applicable",
  "triggered": true,
  "added_nodes": [],
  "removed_nodes": [],
  "changed_nodes": [],
  "impact": "none | low | medium | high",
  "confirmation_ref": "APF-RC8-xx"
}
```

## Pass criteria

The gate passes only when every process-affecting node change is either:

```text
confirmed
not-applicable
explicitly deferred
```

with a recorded reason.
