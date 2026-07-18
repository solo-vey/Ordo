# Visual Graph Generator Integration Plan

Status: **planned for M61.2**.  
M61.1 documents the plan only and does not import code.

## Candidate utility

Candidate archive reviewed:

```text
ordo_visual_graph_generator_v1_1_annotation_preview.zip
```

The utility is a standalone Python graph renderer for Ordo YAML/IR.

## Recommended first import

Import the current utility with minimal restructuring:

```text
utilities/ordo_visual_graph_generator/
  README.md
  ORDO_GRAPH_INPUT_CONTRACT.md
  GRAPH_OUTPUT_LAYERS.md
  ANNOTATION_OVERLAY_SCHEMA.md
  TRACE_OVERLAY_SCHEMA.md
  ordo_graph.py
  ordo_graph_annotation_demo.py
  ordo_graph_with_attached_gates.py
  examples/
  reference_outputs/
  tests/
```

Do not immediately merge it into PathWalk and do not make it part of the runtime CLI.

## Acceptance checks for M61.2

- `py_compile` passes for imported Python files;
- existing utility tests pass or any environment-only failures are documented;
- Mermaid `.mmd` smoke passes without Graphviz;
- SVG/PNG smoke passes when Graphviz `dot` is available;
- README documents dependencies (`pyyaml`, optional Graphviz);
- no Ordo runtime-core files are changed;
- no scoring weights or benchmark runner behavior is changed.

## Compatibility rule

Visual Graph Generator is a read-only renderer:

```text
Ordo YAML/IR → graph artifacts
```

It must not claim runtime validation, execute a session, call an LLM/MCP, or mutate source YAML.
