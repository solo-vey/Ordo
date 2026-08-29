# Visual Graph Generator Integration Plan

Status: **completed in M61.2 as minimal package import**.

## Imported utility

Source archive reviewed and imported:

```text
ordo_visual_graph_generator_v1_1_annotation_preview.zip
```

Imported location:

```text
utilities/ordo_visual_graph_generator/
```

M61.2 preserves the standalone utility shape rather than merging it into PathWalk or the Ordo runtime CLI.

## Included files

```text
README.md
ORDO_GRAPH_INPUT_CONTRACT.md
GRAPH_OUTPUT_LAYERS.md
ANNOTATION_OVERLAY_SCHEMA.md
TRACE_OVERLAY_SCHEMA.md
ORDO_INTEGRATION_NOTES.md
ordo_graph.py
ordo_graph_annotation_demo.py
ordo_graph_with_attached_gates.py
examples/
reference_outputs/
tests/
```

## Acceptance checks

M61.2 acceptance requires:

- `py_compile` for imported Python files;
- existing utility pytest;
- Mermaid `.mmd` smoke;
- SVG smoke when Graphviz `dot` is available;
- annotation overlay smoke when Graphviz `dot` is available;
- package documentation updated;
- no Ordo runtime-core semantics changed;
- no PathWalk feature behavior changed;
- no runtime execution/scoring/calibration introduced.

## Compatibility rule

Visual Graph Generator is a read-only renderer:

```text
Ordo YAML/IR → graph artifacts
```

It must not claim runtime validation, execute a session, call an LLM/MCP, or mutate source YAML.
