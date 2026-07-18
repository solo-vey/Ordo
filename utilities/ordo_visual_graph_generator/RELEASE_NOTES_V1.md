# Ordo Visual Graph Generator v1

This is the first packaged version of the Ordo Visual Graph Generator utility.

## Scope

The utility renders Ordo YAML/IR as visual graphs with stable output formats:

```text
mmd
svg
png
```

## Included v1 capabilities

- Main workflow tree rendering.
- Branch label resolution.
- SVG/PNG rendering through Graphviz `dot`.
- Structural validation for missing/unknown targets.
- Support for both `steps:` and `nodes:` style Ordo inputs.
- Focus/subtree/context/path modes in the utility implementation.
- Artifact/package rendering modes.
- Gate support and attached gate views.
- Documentation for all reviewed graph output layers.
- Trace overlay schema `ordo.graph.trace.v2`.
- Reference SVGs for:
  - full all-layers graph
  - contract details v2
  - state schema coverage clean
  - gate detail cards
  - includes/freeform details
  - artifact coverage readiness
  - trace overlay v2

## Important rendering principle

```text
Attach metadata near the node when it belongs to that node.
Use a global cluster only for data that cannot be attached.
Avoid unreadable fan-out lines from global summary nodes.
```

## Notes

The reference YAML used during validation contains `outputs[]` and document bullets, but does not contain top-level canonical artifact fields such as `artifacts[]`, `artifact_requirements[]`, `coverage_rules[]`, `rendered_artifact_assertions[]`, or `go_no_go`. These are documented as planned/contract-supported input fields.


## Example data policy

The release package contains only imaginary/demo Ordo examples.

Real project-specific test cases used during development are not included as samples, reference outputs, or documentation examples.
