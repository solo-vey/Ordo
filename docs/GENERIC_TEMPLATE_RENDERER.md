# Generic Template Renderer (M79.2)

`ordo template render` is the single renderer interface for all generic template modes.

```bash
ordo template render CONTRACT --input INPUT.yaml --output-dir OUTPUT
```

- `deterministic`: renders the declared `template_ref` locally and writes render evidence.
- `model_rendered`: does not invoke a model implicitly; it creates `model_render_job.json` with an immutable input snapshot, prompt reference, output contract, review profile, and provenance requirements.
- `hybrid`: renders a deterministic scaffold and creates a controlled model-completion job.

Every successful run writes `render_evidence.json` with contract and input SHA-256 values. Missing required inputs, type mismatches, path escape, missing source files, or unresolved placeholders fail closed.
