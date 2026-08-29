# Ordo Integration Notes — Visual Graph Generator

Status: **included companion utility as of M61.2**.

This directory imports the standalone Visual Graph Generator with minimal restructuring. The first import intentionally preserves the original scripts, examples, contracts, and tests rather than merging the utility into PathWalk or the Ordo runtime CLI.

## Role

```text
Ordo YAML / IR → visual graph artifacts
```

The utility is read-only. It may generate `.mmd`, `.svg`, `.png`, `.dot`, and overlay reports, but it must not mutate source YAML, execute a runtime session, call an LLM/MCP, score model behavior, or claim runtime validation.

## Basic commands

From the repository root:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py \
  utilities/ordo_visual_graph_generator/examples/demo_support_triage.ordo.yaml \
  --format mmd \
  --out runs/visual_graph/demo_support_triage.mmd
```

SVG rendering requires Graphviz `dot`:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py \
  utilities/ordo_visual_graph_generator/examples/demo_support_triage.ordo.yaml \
  --format svg \
  --out runs/visual_graph/demo_support_triage.svg
```

Annotation overlay demo:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph_annotation_demo.py \
  utilities/ordo_visual_graph_generator/examples/demo_support_triage.ordo.yaml \
  --annotations utilities/ordo_visual_graph_generator/examples/demo_support_triage.annotations.v1.json \
  --out runs/visual_graph/demo_support_triage_annotation_overlay.svg
```

## Relationship to PathWalk

PathWalk generates test/review artifacts. Visual Graph Generator renders structural diagrams. They are companion utilities at the same layer, but they remain separate tools. A future consolidation milestone may add cross-links or a unified utility quickstart, but M61.2 does not merge their internals.
