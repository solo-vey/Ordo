# Ordo Graph Trace Overlay Schema

Schema id:

```text
ordo.graph.trace.v2
```

Purpose:

```text
Overlay an actual user/model traversal onto a static Ordo workflow graph.
```

The trace file is produced before graph generation. The graph renderer uses it to highlight the exact path the user/model followed.

## Why v2 exists

The first trace overlay highlighted edges only by:

```text
source node -> target node
```

That is not precise enough. In Ordo, several branches may share the same target node.

Example:

```text
N1 -- A --> N2
N1 -- B --> N2
N1 -- F --> N2
```

If the trace only says `N1 -> N2`, all three edges may be highlighted.

Therefore v2 identifies the branch using:

```text
node_id
answer_key
next_node_id
```

## Minimal schema

```json
{
  "schema": "ordo.graph.trace.v2",
  "run_id": "demo_demo_support_triage_path_A_precise",
  "steps": [
    {
      "node_id": "N1_PATH_SELECTION",
      "answer_key": "A",
      "next_node_id": "N2_SOURCE_CONTRACT",
      "branch_comment": "Вибрав A, бо зміна стосується demo source system / фактографії.",
      "node_comment": "Стартовий вибір маршруту."
    }
  ]
}
```

## Fields

### `schema`

Required.

```text
ordo.graph.trace.v2
```

### `run_id`

Required string.

A stable id for the traversal run.

### `steps`

Required list.

Each step describes one node visit and optionally one outgoing branch.

### `steps[].node_id`

Required string.

The Ordo node being visited.

### `steps[].answer_key`

Optional string or null.

The exact branch key chosen at this node.

Examples:

```text
A
B
yes
no
1
```

For free-text nodes with direct `next`, this may be null.

### `steps[].next_node_id`

Optional string.

The next node reached after the answer.

This is used together with `answer_key` to avoid highlighting sibling branches that share the same target.

### `steps[].node_comment`

Optional string.

A comment attached to the node card.

Use this for:

```text
what the user/model confirmed at this node
why this node was considered complete
what was unclear at this node
```

### `steps[].branch_comment`

Optional string.

A comment attached to the selected branch/edge.

Use this for:

```text
why this answer was chosen
what clarification was given with the answer
whether the model almost took a wrong branch
```

## Highlighting behavior

The renderer should highlight:

```text
node_id card
edge matching (node_id, answer_key, next_node_id)
node_comment note
branch_comment note
```

It must not highlight all edges with the same source and target.

## Validation rules

A trace overlay should be validated before rendering:

```text
Every node_id must exist in the YAML.
Every next_node_id must exist or be a terminal/gate target.
If answer_key is not null, it must exist under that node's on_answer/branches.
The tuple (node_id, answer_key, next_node_id) must match an actual edge.
Branch comments may exist only when a branch/edge exists.
Node comments may exist for any visited node.
```

## Future extension

The schema can later add:

```json
{
  "result": "completed | stopped | escalated | failed",
  "model_confusion_events": [],
  "repair_attempts": [],
  "timestamps": [],
  "evidence": []
}
```

This would allow the same trace file to support both graph overlay and model-behavior testing.
