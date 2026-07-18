# Template-based output generation

M8 moves generated markdown artifacts out of hardcoded Python package logic and into the Ordo package itself.

A package can define:

```text
output_templates/
  output_templates.yaml
  templates/
    contract.md
    handoff.md
```

The CLI command:

```bash
ordo generate-output <package>
```

renders those templates using the latest `run` or `intake` state. It does not call an AI model and does not invent missing content.

## Placeholder examples

```text
{{ state.event_alias }}
{{ state.qa_scope | bullets }}
{{ state.approval_received | bool_lower }}
{{ package.name }}
{{ generated_at }}
{{ gate_summary.passed }}
```

Supported filters in v0.4.0:

- `bullets`
- `safe_name`
- `bool_lower`
- `json`

## Rule

The Ordo Source remains the source of truth. Generated outputs are derived artifacts.
