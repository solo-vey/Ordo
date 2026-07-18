# Ordo Two-Tier Rendering Model

Ordo output templates use an explicit rendering boundary so the CLI does not pretend to render templates that require model reasoning.

## Rendering modes

### `render_mode: deterministic`

Deterministic templates are rendered by the CLI renderer `ordo.simple`.

Required metadata:

```yaml
render_mode: deterministic
renderer: ordo.simple
requires_model_rendering: false
```

Allowed syntax:

```text
{{ state.scalar }}
{{ state.list | bullets }}
{{ state.value | safe_name }}
{{ state.object | json }}
```

Forbidden syntax:

```text
{% for %}
{% if %}
loop.index
.items()
| default("...")
```

If a deterministic template contains unsupported syntax, `ordo lint` and `ordo generate-output` fail with `ORDO-RENDER-001`.

## `render_mode: model_assisted`

Model-assisted templates are complex templates that must be rendered by an AI model and then deterministically validated.

Required metadata:

```yaml
render_mode: model_assisted
renderer: ai.markdown # or ai.yaml / ai.json
requires_model_rendering: true
validation: strict_confirmed_state_only
tbd_policy: preserve_tbd_until_confirmed
```

Model-assisted rendering may use only:

```text
confirmed_state
explicit_tbd_defaults
```

It must not:

```text
infer_missing_values
mark_candidate_as_confirmed
remove_tbd_markers_without_confirmation
```

## Runtime flow

```text
output_templates                  -> deterministic -> ordo.simple -> generated artifact
model_assisted_output_templates   -> model handoff -> AI render -> validate-artifacts
```

`ordo generate-output` creates handoff packets for model-assisted templates under:

```text
runtime/model_assisted_render_handoff/<ARTIFACT_ID>.json
```

The packet contains the template content, confirmed state, expected output path, TBD policy, forbidden inference rules and post-validation requirements.

## Validation errors

```text
ORDO-RENDER-001 deterministic template contains unsupported syntax
ORDO-RENDER-002 model-assisted template rendered by simple renderer
ORDO-RENDER-003 model-assisted output contains inferred unconfirmed value
ORDO-RENDER-004 TBD marker removed without confirmed state
ORDO-RENDER-005 model-assisted YAML/JSON output is invalid
ORDO-RENDER-006 model-assisted output not validated / unresolved template syntax remains
```

## Relation to M46

M46 validates contract coverage and rendered artifacts. M52 adds the rendering boundary before artifacts are produced:

```text
template complexity -> rendering mode -> handoff/render -> deterministic validation -> consistency -> go/no-go
```
