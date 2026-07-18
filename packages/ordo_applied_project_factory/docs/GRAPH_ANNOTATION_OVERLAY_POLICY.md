# Graph Annotation Overlay Policy

Default working visualization remains focused/context SVG:

```text
root → current node → subtree below current node
```

The `ordo_visual_graph_generator 1.1.0-preview` annotation overlay may be used when helpful to show review comments directly on the graph.

## Use annotations for

- highlighting a newly changed node;
- marking a gate or state field that needs review;
- explaining why a node exists;
- marking important authoring decisions.

## Do not use annotations as

- source of truth;
- semantic validation;
- replacement for YAML, gates, tests, or CLI reports.

## Annotation schema

```text
ordo.graph.annotations.v1
```

Supported targets include `node`, `edge`, `gate`, `state`, `output`, and related graph elements.
