# Chapter 47. Two-tier Rendering Model

By this point, Ordo can already verify whether confirmed contracts reached generated artifacts. But another problem appears: not all output templates are the same.

Some templates are simple. They contain only substitutions such as `{{ state.alias }}` or `{{ state.list | bullets }}`. The CLI can safely render them.

Other templates are complex. They contain loops, conditions, tables, traceability matrices, nested YAML blocks, or manual QA/automation scenarios. A simple deterministic renderer should not render such templates.

Ordo therefore introduces a two-tier rendering model.

## Tier one: deterministic rendering

A deterministic template is fully supported by the `ordo.simple` CLI renderer.

```yaml
render_mode: deterministic
renderer: ordo.simple
requires_model_rendering: false
```

It allows simple substitutions:

```text
{{ state.scalar }}
{{ state.list | bullets }}
{{ state.value | safe_name }}
{{ state.object | json }}
```

But constructs such as these are forbidden:

```text
{% for %}
{% if %}
loop.index
.items()
| default("...")
```

If such a construct appears in a deterministic template, `ordo lint` or `ordo generate-output` must fail. The CLI must not pretend to understand complex AI templates.

## Tier two: model-assisted rendering

A model-assisted template is rendered by an AI model.

```yaml
render_mode: model_assisted
renderer: ai.markdown
requires_model_rendering: true
validation: strict_confirmed_state_only
tbd_policy: preserve_tbd_until_confirmed
```

The CLI does not render such a template directly. Instead, it creates a handoff packet:

```text
runtime/model_assisted_render_handoff/<ARTIFACT_ID>.json
```

The packet contains:

- template content;
- confirmed state;
- expected output path;
- TBD policy;
- forbidden inference rules;
- post-validation requirements.

The AI may fill a complex Markdown/YAML/JSON artifact, but it may not invent missing values.

## Main rule

Model-assisted rendering may use only confirmed state and explicit TBD defaults.

If a value is not confirmed, it must remain:

```text
⚠️ TBD
```

The AI may not remove TBD merely because a value “seems obvious.”

## Post-validation

After AI rendering, Ordo returns to deterministic mode:

```text
validate-artifacts → consistency → go-no-go
```

The system checks:

- whether unresolved placeholders remain;
- whether YAML/JSON is valid;
- whether confirmed values match state;
- whether inferred values appeared;
- whether TBD was removed without confirmation.

The two-tier rendering model creates an honest boundary: the model may help with a complex document, but final verification becomes deterministic again.

## Standard rendering-layer errors

```text
ORDO-RENDER-001 deterministic template contains unsupported syntax
ORDO-RENDER-002 model-assisted template rendered by simple renderer
ORDO-RENDER-003 model-assisted output contains inferred unconfirmed value
ORDO-RENDER-004 TBD marker removed without confirmed state
ORDO-RENDER-005 model-assisted YAML output is invalid
ORDO-RENDER-006 model-assisted output not validated after rendering
```
