# Generic Template and Review Tooling

## Purpose

The generic template layer separates reusable output-template contracts from individual playbooks. A playbook references a stable `template_id`, while the Ordo CLI validates the template contract, selects a render mode, and later supplies rendering, review, diff, test, and registry operations.

## Render modes

- `deterministic`: rendered entirely by deterministic tooling.
- `model_rendered`: the CLI prepares a controlled model job and validates the returned artifact.
- `hybrid`: deterministic structure plus explicitly bounded model-rendered sections.

## Current command

```bash
ordo template validate path/to/template.yaml
```

The command validates identity, semantic version, render mode, input/output contracts, review profile, compatibility, and model-specific requirements. It writes `template_validation_report.json` next to the contract unless `--out` is supplied.

## Planned command family

```bash
ordo template registry-check
ordo template render
ordo template review
ordo template diff
ordo template test
```

## Documentation rule

Every new template capability must update all three layers in the same milestone:

1. machine-readable schema and CLI behavior;
2. developer documentation and examples;
3. the Ordo book or its appendices.

A milestone is not complete when code changes but documentation/book coverage is missing.
