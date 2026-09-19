# Documentation Graph Synchronization

Executable routes are the source of truth for pseudo-chat documentation. The CLI can generate a deterministic Markdown view and reject a document that describes a removed, unreachable, or undocumented route.

## Generate the view

```bash
PYTHONPATH=cli python -m ordo generate-pseudo-chat path/to/package
```

The default output is `docs/PSEUDO_CHAT.md` inside the package. Use `--out FILE.md` to write elsewhere.

Each generated vertex and transition has an HTML marker. The markers make the view reviewable as ordinary Markdown while allowing a validator to compare it exactly with the executable graph.

## Validate the view

```bash
PYTHONPATH=cli python -m ordo validate-documentation-graph path/to/package
```

The command writes `reports/documentation_graph_report.json` by default and fails when the document is missing, a documented node or gate was removed or is unreachable, or a reachable node or transition is undocumented. Use `--document FILE.md` and `--out REPORT.json` to override defaults.

This command is deliberately separate from `lint`: a package opts into maintaining a pseudo-chat view by generating and validating one, without making existing packages fail solely because they do not yet publish that view.
