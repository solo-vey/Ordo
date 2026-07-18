# CLI: Two-Tier Rendering

`ordo generate-output` now separates deterministic templates from model-assisted templates.

## Deterministic templates

Rendered directly by CLI:

```yaml
output_templates:
  - id: SUMMARY_JSON
    render_mode: deterministic
    renderer: ordo.simple
    requires_model_rendering: false
```

Unsupported syntax such as `{% for %}`, `{% if %}`, `loop.index`, `.items()` and complex `default(...)` causes:

```text
ORDO-RENDER-001
```

## Model-assisted templates

Not rendered by CLI. Instead, CLI creates a handoff packet:

```yaml
model_assisted_output_templates:
  - id: QA_AUTOMATION_SPEC
    render_mode: model_assisted
    renderer: ai.yaml
    requires_model_rendering: true
    validation: strict_confirmed_state_only
    tbd_policy: preserve_tbd_until_confirmed
```

Handoff packets are written to:

```text
runtime/model_assisted_render_handoff/
```

## Post-render validation

After an AI model renders the handoff into the expected output file, run:

```bash
ordo validate-artifacts <package>
ordo consistency <package>
ordo go-no-go <package>
```

`validate-artifacts` checks unresolved template syntax, YAML/JSON parseability, confirmed-state consistency, forbidden unconfirmed terms and TBD preservation.
