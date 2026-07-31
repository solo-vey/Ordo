# Ordo Tree Editor

Ordo Tree Editor is a local visual companion utility for editing an Ordo
playbook graph. It opens a browser interface on your own computer and does not
send YAML or process data to a hosted service.

## What the 0.2.0 alpha provides

- open an Ordo YAML file and display its nodes, executable gates, terminal
  outcomes, and transitions;
- distinguish interactive nodes, separate top-level gates, and external
  terminal/output targets in the graph;
- select, move, add, edit, and delete complete node and gate records without
  dropping their unknown top-level blocks;
- inspect each node as structured YAML fields or as one live full-YAML view;
- create a transition by hovering a source node, choosing **Add transition**,
  then clicking its target node;
- remove a node or gate route by hovering its line and choosing **Delete
  transition**;
- show both canonical `on_answer` and ARF-style `transitions` routes;
- show canonical list-based `transitions` entries (`to:`) and
  `navigation_contract.allowed_to` routes without duplicating edges;
- show gate `on_pass`/`on_fail` and canonical `pass_to`/`fail_to` routes with
  explicit edge labels;
- show top-level `terminals:` records as terminal targets;
- use question, gate, materialization, and terminal-node starters;
- inspect the reusable ARF tree-module catalog;
- run the existing Ordo graph and lint validators locally;
- export ordinary YAML for further work in a chat or repository.

The graph layout is editor-local: moving nodes changes the canvas only and
does not add visual-layout metadata to the YAML source.

## Run locally

Requirements: Python 3.10+ and the normal Ordo CLI dependencies, including
PyYAML. No Docker, Node, cloud account, or API key is required.

From the repository root:

```bash
python3 utilities/ordo_tree_editor/editor_service.py
```

The editor opens at `http://127.0.0.1:8765`. On macOS, double-click
`start_ordo_tree_editor.command` after making it executable, or run it from a
terminal.

To choose a different port or avoid opening a browser automatically:

```bash
python3 utilities/ordo_tree_editor/editor_service.py --port 9000 --no-browser
```

## Validation boundary

The editor calls the canonical Python graph and lint validators locally. It
does not silently repair a graph, materialize a reusable module, invoke a
model, or change package runtime behavior. Use the normal Ordo CLI for
package compilation, full test execution, release validation, and explicit
tree-module instantiation.

## Distribution model

The source utility is shipped in the repository and can be packed into a
versioned ZIP release. Version `0.2.0-alpha.2` is an alpha test build: use it
to review and edit local copies, then validate the exported YAML through the
normal Ordo controls before relying on it. It requires an installed Python
runtime. A later desktop-distribution phase may bundle Python into a macOS
`.app` or Windows application; that packaging concern is intentionally
separate from the editor and validator contracts.
