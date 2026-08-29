# ORDO_GRAPH_INPUT_CONTRACT.md

## Purpose

This document defines how **Ordo Visual Graph Generator** reads Ordo YAML/IR files.

The graph utility is a standalone review/debug tool. It is **not** part of the Ordo core runtime and must not execute workflows.

## Non-goals

The graph utility must not:

- execute runtime nodes;
- call LLM;
- call MCP;
- mutate source YAML/IR;
- claim business/semantic validation passed;
- invent missing workflow content.

## Supported source forms

The utility should support two source shapes.

### 1. Authoring YAML with `nodes`

Canonical guided-intake form:

```yaml
nodes:
  - id: N1_PATH_SELECTION
    question: "..."
    answer_type: enum
    allowed_answers: [A, B, C]
    on_answer:
      A:
        next: N2_SOURCE_CONTRACT
        update_state:
          selected_path: A
```

### 2. Workflow YAML with `steps`

Simpler workflow form:

```yaml
steps:
  - id: intake
    type: ask
    next: classify
  - id: classify
    type: decide
    branches:
      A:
        next: finish
```

## Node rendering rules

All workflow blocks should render as readable rectangles by default.

Recommended node label:

```text
<node.id>
<short first question/title/label line>
```

Do not render the full question body inside the block unless a verbose/debug mode is explicitly added later.

## Edge rendering rules

### Enum branches

Branch labels should be human-readable.

Resolution order:

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
13. raw key, for example `A` or `1`

### Free-text direct transitions

A direct `on_answer.next` edge for a `free_text` node should have **no label by default**.

Do not show technical labels like:

```text
answer
```

Only show a label when the YAML explicitly provides one of:

```yaml
transition_label: ...
edge_label: ...
label: ...
```

## Target resolution rules

A transition target may point to:

- another `nodes[].id`;
- another `steps[].id`;
- terminal symbolic node:
  - `STOP_*`
  - `ERROR_*`
  - `REPAIR_*`
  - `error:*`
  - `repair:*`
  - `terminal:*`
- gate id from top-level `gates[]`.

Unknown targets are structural errors and must block graph generation.

## Gates

Top-level `gates[]` are first-class graph targets.

A gate should render as a node when:

- a workflow transition points to it;
- `outputs[].allowed_after` references it in coverage mode;
- gate display mode is enabled later.

Basic gate label:

```text
<gate.id>
Gate
```

## Artifacts

### Canonical source

If the YAML/IR contains top-level `artifacts[]`, it is the canonical source for concrete document/artifact nodes.

Expected fields include some combination of:

```yaml
artifacts:
  - id: HISTORY_EVENT_PASSPORT
    kind: artifact
    path_pattern: 01_HISTORY_EVENT_PASSPORT_<ALIAS>.md
    format: markdown
```

Graph label preference:

1. `path_pattern`
2. `path`
3. `title`
4. `name`
5. `id`

### Branch-level artifacts

If `on_answer.<key>.artifacts` or `output_artifacts` exists, render those artifacts after the target terminal node.

### Outputs are containers

Top-level `outputs[]` often describes package/archive outputs, not individual documents.

Do not render one vague document node from `outputs[]` when concrete `artifacts[]` exists.

Render `outputs[]` as package/archive/container nodes only in package or coverage modes.

### Fallback artifact extraction

For legacy YAML where concrete artifacts are only listed in a question body, the utility may extract bullet lines that look like file/document names:

```text
- 01_HISTORY_EVENT_PASSPORT_<ALIAS>.md
- 02_JIRA_TASK_<ALIAS>.md
```

This fallback is weaker than canonical `artifacts[]` and should be treated as compatibility behavior.

## Artifact requirement coverage

If `artifact_requirements[]` exists, coverage mode should connect:

```text
contract/gate/assertion → artifact_requirement → artifact
```

This is not required for normal workflow view.

## Partial rendering

The utility supports focused rendering.

### Full tree

No focus parameters:

```bash
python ordo_graph.py input.ordo.yaml --format svg --out full.svg
```

### Subtree

Selected node and everything reachable after it:

```bash
python ordo_graph.py input.ordo.yaml --start N2_SOURCE_CONTRACT --format svg --out subtree.svg
```

### Context

Direct path from root to focused node, then subtree after focused node:

```bash
python ordo_graph.py input.ordo.yaml --focus N3_EVENT_IDENTITY_CONTRACT --mode context --format svg --out context.svg
```

### Path

Only direct path from root to focused node:

```bash
python ordo_graph.py input.ordo.yaml --focus N3_EVENT_IDENTITY_CONTRACT --mode path --format svg --out path.svg
```

## Supported output formats

Only these are supported for now:

```text
mmd
svg
png
```

## Validation report

The utility should print a readable structural validation report and block generation on errors.

Required checks:

- missing `nodes`/`steps`;
- malformed `nodes`/`steps`;
- missing ids;
- duplicate ids;
- invalid branches;
- unknown transition targets;
- unknown `--start` / `--focus`;
- invalid partial rendering mode;
- missing Graphviz `dot` for `svg/png`.

## CLI help

The utility must support:

```bash
python ordo_graph.py --help
```

Help should explain:

- formats;
- input file;
- output file;
- partial rendering;
- artifact rendering mode;
- examples.

## Planned artifact modes

Not all modes must be implemented in the first pass.

```text
--artifact-mode none
--artifact-mode terminal
--artifact-mode package
--artifact-mode coverage
--artifact-mode all
```

Recommended default:

```text
terminal
```

Meaning:

- `none`: do not render artifacts.
- `terminal`: render branch/terminal concrete artifacts.
- `package`: render top-level package/archive outputs.
- `coverage`: render artifact requirements and contract/gate coverage.
- `all`: render all supported artifact/package/coverage views.

## Current implementation priority

### P0

- smart branch labels;
- no noisy `answer` labels;
- gate ids as valid targets;
- canonical `artifacts[]` support;
- outputs as package/archive containers, not fake documents;
- partial rendering modes.

### P1

- `--artifact-mode`;
- `--gate-mode`;
- `--show-unmatched`;
- richer validation report.

### P2

- compiled Semantic JSON IR / `GATE.DEF` / `OUTPUT.DEF` support.
