# Ordo Tree Editor

Ordo Tree Editor is a local visual companion utility for editing an Ordo
playbook graph. It opens a browser interface on your own computer and does not
send YAML or process data to a hosted service.

## What V1 provides

- open an Ordo YAML file and display its nodes and transitions;
- select, move, add, edit, and delete basic nodes;
- add transitions while keeping `allowed_from` symmetric;
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
versioned ZIP release. The current source distribution is published at
`ordo-tree-editor-v0.1.0` beside its SHA-256 file. V1 requires an installed Python runtime. A later
desktop-distribution phase may bundle Python into a macOS `.app` or Windows
application; that packaging concern is intentionally separate from the editor
and validator contracts.
