# DD-ORDO-M52-001 — Two-Tier Rendering Model

## Status

Accepted for `v0.12.0-preview-rc1` package line.

## Context

The `ordo.simple` renderer is intentionally small and deterministic. It supports simple state substitutions and a few filters, but it must not render complex AI-oriented templates with loops, conditions, traceability matrices, nested YAML blocks or model-dependent wording.

## Decision

Ordo output templates now declare an explicit rendering mode:

- `render_mode: deterministic` with `renderer: ordo.simple`.
- `render_mode: model_assisted` with `renderer: ai.markdown`, `ai.yaml` or `ai.json`.

`ordo generate-output` renders only deterministic templates. Model-assisted templates are converted into handoff packets under `runtime/model_assisted_render_handoff/`.

After AI rendering, deterministic post-validation is performed through `validate-artifacts`, `consistency`, and `go-no-go`.

## Consequences

- CLI no longer silently simple-renders complex templates.
- Unsupported deterministic syntax is caught by `lint` / `generate-output`.
- AI-rendered artifacts remain auditable through confirmed-state checks.
- Missing values must remain `⚠️ TBD` until confirmed.
