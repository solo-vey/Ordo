# Ordo Visual Graph Generator

Standalone Python utility for rendering an Ordo YAML/IR workflow as a visual graph.

This tool is for **review, debugging, explanation, and visual inspection** of Ordo workflows. It is intentionally separate from the Ordo core runtime.

## What it does

The utility reads an Ordo YAML/IR file and generates:

```text
graph.mmd
graph.svg
graph.png
```

It can render:

- full workflow trees;
- focused subtrees;
- context views: direct path from root to a node plus everything below that node;
- path-only views;
- enum branch labels;
- free-text transitions without noisy technical labels;
- terminal/repair/error paths;
- gate ids referenced by transitions;
- terminal artifacts/documents;
- package/archive outputs.

## What it does not do

The utility does **not**:

- execute the workflow;
- call LLM;
- call MCP;
- mutate or rewrite source YAML;
- validate business semantics;
- claim runtime validation passed.

It performs structural graph validation only.

## Supported formats

```text
mmd
svg
png
```

SVG/PNG rendering uses Graphviz `dot`.

## Installation requirements

Python dependency:

```bash
pip install pyyaml
```

Image rendering dependency:

```bash
dot -V
```

Install Graphviz if `dot` is missing.

macOS:

```bash
brew install graphviz
```

Ubuntu/Debian:

```bash
sudo apt-get install graphviz
```

## Basic usage

Generate SVG:

```bash
python ordo_graph.py input.ordo.yaml --format svg --out graph.svg
```

Generate PNG:

```bash
python ordo_graph.py input.ordo.yaml --format png --out graph.png
```

Generate Mermaid:

```bash
python ordo_graph.py input.ordo.yaml --format mmd --out graph.mmd
```

If `--format` is omitted, it is inferred from the `--out` extension:

```bash
python ordo_graph.py input.ordo.yaml --out graph.svg
```

## Partial rendering

Large Ordo workflows can be hard to read as one full graph. Use partial rendering.

### Full tree

```bash
python ordo_graph.py input.ordo.yaml --format svg --out full.svg
```

### Subtree

Render a selected node and everything reachable after it:

```bash
python ordo_graph.py input.ordo.yaml \
  --start N2_SOURCE_CONTRACT \
  --format svg \
  --out subtree.svg
```

`subtree` is the default mode.

### Context view

Render the direct path from root to the selected node, then render the full subtree below that node:

```bash
python ordo_graph.py input.ordo.yaml \
  --focus N3_EVENT_IDENTITY_CONTRACT \
  --mode context \
  --format svg \
  --out context.svg
```

Example meaning:

```text
ENTRY/root → ... → N3_EVENT_IDENTITY_CONTRACT
then all descendants below N3_EVENT_IDENTITY_CONTRACT
```

### Path-only view

Render only the direct path from root to the selected node:

```bash
python ordo_graph.py input.ordo.yaml \
  --focus N3_EVENT_IDENTITY_CONTRACT \
  --mode path \
  --format svg \
  --out path.svg
```

### Depth limit

Limit descendants in `subtree` or `context` mode:

```bash
python ordo_graph.py input.ordo.yaml \
  --start N2_SOURCE_CONTRACT \
  --depth 2 \
  --format svg \
  --out subtree_depth_2.svg
```

## Artifact rendering

Artifact rendering is controlled by:

```bash
--artifact-mode none|terminal|package|all
```

Default:

```text
terminal
```

Modes:

| Mode | Meaning |
|---|---|
| `none` | Do not render artifacts or outputs. |
| `terminal` | Render branch-level artifacts and compatibility-extracted terminal document bullets. |
| `package` | Render top-level `outputs[]` as package/archive containers. |
| `all` | Render terminal artifacts, canonical `artifacts[]`, and package outputs. |

Examples:

```bash
python ordo_graph.py input.ordo.yaml \
  --artifact-mode terminal \
  --format svg \
  --out terminal_artifacts.svg
```

```bash
python ordo_graph.py input.ordo.yaml \
  --artifact-mode package \
  --format svg \
  --out packages.svg
```

## Branch labels

The utility resolves branch labels in this order:

1. `on_answer.<key>.label`
2. `on_answer.<key>.title`
3. `on_answer.<key>.text`
4. `on_answer.<key>.description`
5. `answer_options.<key>`
6. `options.<key>`
7. option lines parsed from `question`, for example:
   - `A — text`
   - `B - text`
   - `1. text`
   - `2) text`
8. `on_answer.<key>.update_state.selected_path_label`
9. `on_answer.<key>.update_state.test_coverage_level`
10. `on_answer.<key>.update_state.coverage_level`
11. `on_answer.<key>.update_state.*_label`
12. object-style `allowed_answers`
13. raw key, such as `A` or `1`

## Free-text transitions

Direct transitions from free-text nodes are unlabeled by default.

The utility intentionally avoids rendering a noisy technical label like:

```text
answer
```

To force a label, use one of:

```yaml
transition_label: ...
edge_label: ...
label: ...
```

## Gates

Top-level `gates[]` are valid transition targets. If a node points to a gate id, the graph renders that gate as a node.

## Outputs and artifacts

Important distinction:

- `artifacts[]` describes concrete documents/files.
- `outputs[]` often describes package/archive containers.
- question text bullets may contain legacy document lists.

The utility prefers concrete `artifacts[]` when available. It renders `outputs[]` as package/archive containers, not as fake individual documents.

## Validation

The utility blocks generation on structural errors.

It checks:

- missing workflow list;
- malformed `nodes:` or `steps:`;
- missing ids;
- duplicate ids;
- invalid branches;
- unknown transition targets;
- unknown `--start` or `--focus`;
- invalid mode;
- missing Graphviz `dot` for SVG/PNG.

Example:

```text
Validation report:
- [ERROR] UNKNOWN_TARGET at nodes[3].on_answer.A: Unknown target: N99_MISSING
Summary: 1 error(s), 0 warning(s).
Graph generation blocked because structural validation has errors.
```

## Help

```bash
python ordo_graph.py --help
```

## Examples included

```text
examples/
  demo_support_triage.ordo.yaml
  program_error_user_survey_with_artifacts.ordo.yaml
  p0_history_A_context_terminal.svg
  p0_history_A_context_terminal.png
  p0_history_A_context_terminal.mmd
  p0_history_A_context_package.svg
  p0_test_subtree_startup.svg
```

## Source contract

See:

```text
ORDO_GRAPH_INPUT_CONTRACT.md
```

That file defines the graph utility input contract and fallback rules.

## Documentation update: graph layers and trace overlay

The graph generator now documents the supported overlay layers and trace overlay format:

- `GRAPH_OUTPUT_LAYERS.md` — supported information types, source YAML fields, attachment rules, and readability constraints.
- `TRACE_OVERLAY_SCHEMA.md` — `ordo.graph.trace.v2` format for highlighting the exact user/model path, including selected branch and comments.

Important rendering rule:

```text
Attach metadata near the node when it belongs to that node.
Use a separate global cluster only for metadata that cannot be attached.
Do not render huge fan-out edges from summary nodes when the same status can be embedded in cards.
```



## Demo examples

The `examples/` directory contains imaginary examples only:

```text
examples/demo_support_triage.ordo.yaml
examples/demo_support_triage.trace.v2.json
reference_outputs/demo_support_triage_full.svg
```

No real project-specific test case is included in the v1 package.

## Annotation overlay demo renderer

`ordo_graph_annotation_demo.py` demonstrates `ordo.graph.annotations.v1` rendering.

```bash
python ordo_graph_annotation_demo.py \
  examples/demo_support_triage.ordo.yaml \
  --annotations examples/demo_support_triage.annotations.v1.json \
  --out reference_outputs/demo_support_triage_annotation_overlay.svg
```
