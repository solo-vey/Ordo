# alpha.20.0.76-dev — unified Replay / Print renderer

UI/print-only R3 refinement.

- `Print / Save PDF` no longer uses a separately styled replay document.
- The print window loads the same `styles.css` used by `Replay Real Chat`.
- The same `.replay-*` DOM/components are reused for header, note, steps, bubbles, gates, analyst responses and values.
- Print-specific CSS now only controls document width, page margins, interaction disabling, and page-flow rules.
- Long replay steps/bubbles may split across physical PDF pages without switching to a different visual design.

No playbook, Compiler, model-call, or runtime execution semantic changes.
