# Chapter 63. Visual Graph Generator as a Companion Utility

Visual Graph Generator is a utility for visually reviewing Ordo programs. It reads `source/program.ordo.yaml` or compatible YAML/IR and creates a graph in Mermaid, SVG, or PNG format.

This utility is not runtime core. It does not execute a session, call a model, modify YAML, or claim that business logic has passed runtime validation. Its role is simpler and very useful: show the process structure so an author, reviewer, or developer can understand it quickly.

## Where it lives

Starting with M61.2, the utility is included in the package at:

```text
utilities/ordo_visual_graph_generator/
```

PathWalk remains alongside it:

```text
ordo_pathwalk/
```

These two utilities should not be merged. PathWalk is responsible for test and review artifacts. Visual Graph Generator is responsible for visually explaining the tree.

## Basic usage

Mermaid graph:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py \
  source/program.ordo.yaml \
  --format mmd \
  --out runs/visual_graph/program.mmd
```

SVG graph, if Graphviz is installed:

```bash
python3 utilities/ordo_visual_graph_generator/ordo_graph.py \
  source/program.ordo.yaml \
  --format svg \
  --out runs/visual_graph/program.svg
```

## Typical author workflow

```text
1. The author writes or receives source/program.ordo.yaml.
2. Visual Graph Generator shows the process tree.
3. The author reviews nodes, transitions, gates, artifacts, and terminal branches.
4. PathWalk generates terminal paths, clean cases, bounded-noise cases, and review cards.
5. Visual Graph annotation overlay can highlight problematic or new graph elements.
```

## Annotation overlay

A separate annotation-overlay mode can highlight graph elements and add comments. This is useful during review: it can show not only a path, but any node, gate, state field, output, or edge that needs attention.

## Responsibility boundary

Visual Graph Generator must remain a read-only utility:

```text
Ordo YAML/IR → graph artifacts
```

It must not become a runtime runner, scorer, or benchmark harness. If automatic execution of generated cases is needed, that must be a separate milestone rather than a hidden expansion of the graph utility.
