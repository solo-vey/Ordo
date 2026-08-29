# alpha.20.0.117-dev

- Focused Data Flow keeps exactly one visible non-transformation entity on the selected semantic layer: the selected entity itself.
- Downstream traversal may pass through hidden same-layer siblings only as transit so later layers remain discoverable; those transit nodes are not rendered.
- Collapsed transit paths render as dashed causal edges.
- Downstream transformations expose supporting prerequisites from earlier semantic layers, including analyst inputs and earlier derived state, without reintroducing same-layer siblings.
- Static package documents/resources are explicitly marked `package_source_resource`; they are valid roots and are not expected to have an upstream producer.
