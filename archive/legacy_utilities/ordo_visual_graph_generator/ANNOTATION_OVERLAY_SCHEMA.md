# Ordo Graph Annotation Overlay Schema

Schema id: `ordo.graph.annotations.v1`

Purpose: highlight and comment any visible graph element, not only the user/model traversal path.

Trace overlay is for the path followed by a user/model.
Annotation overlay is for arbitrary visual notes on graph elements.

## Supported target kinds

`node`, `edge`, `gate`, `assertion`, `state`, `contract`, `repair`, `output`, `artifact`, `include`, `freeform`, `render`, `cluster`.

## Target id conventions

```text
node:<node_id>
edge:<source_node_id>:<answer_key>:<target_node_id>
edge:<source_node_id>::<target_node_id>
gate:<gate_id>
assertion:<assertion_id>
state:<field_name>
contract:<node_id>
repair:<node_id>
output:<output_id>
artifact:<artifact_id_or_filename>
include:<include_as_or_library>
freeform:<freeform_id>
render:<render_id>
cluster:<cluster_id>
```

## Annotation item

```json
{
  "target": "node:N3_USER_CONTEXT",
  "highlight": "new",
  "severity": "notice",
  "source": "manual_review",
  "comment": "New node added in this version."
}
```

Supported `highlight` values:

```text
new
changed
important
warning
review
removed
```

Validation should warn, not crash, when an annotation target cannot be resolved.
