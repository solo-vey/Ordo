# alpha.20.0.54-dev — adaptive composer and file preview

R3 UI-only redesign increment.

- Composer starts as one row between attach and send/stop controls.
- At 2+ visual lines the textarea owns the full upper row and controls move below.
- Standard composer grows to at most 3 lines, then scrolls internally.
- Expand/collapse toggles an approximately 10-line editing surface without losing draft/focus.
- Busy state no longer displays a special placeholder; typing remains available while send is replaced by Stop.
- Markdown generated artifacts render as compact cards with Download and open a read-only right-side Markdown preview.
- Non-Markdown generated artifacts remain download-only links.
- No runtime/playbook semantics changed.
