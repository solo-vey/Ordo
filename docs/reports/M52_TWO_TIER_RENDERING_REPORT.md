# M52 Two-Tier Rendering Report

## Summary

M52 adds a two-tier rendering model for Ordo output templates.

## Changed areas

1. Language/docs:
   - `language/TWO_TIER_RENDERING.md`
   - `language/spec/03_SEMANTIC_JSON_IR.md`
   - `language/schemas/rendering_template_schema.yaml`
   - `language/schemas/semantic_json_ir_schema.yaml`
   - `language/registry/OPCODE_CATALOG.md`

2. CLI/runtime:
   - `cli/ordo/rendering_policy.py`
   - `cli/ordo/output_generator.py`
   - `cli/ordo/artifact_validator.py`
   - `cli/ordo/cli.py`

3. Package examples:
   - `packages/history_event_guided_intake/output_templates/.../output_templates.yaml`
   - `templates/08_qa_automation_spec_model_assisted.yaml`

4. Tests:
   - deterministic template with `{% for %}` fails;
   - model-assisted template with `renderer: ordo.simple` fails;
   - model-assisted templates produce handoff packets;
   - inferred provider class fails post-validation;
   - removed TBD marker fails post-validation;
   - invalid model-assisted YAML fails;
   - confirmed rendered values still pass.

## Self-check

- CLI regression tests: `26/26 OK`.
- Active packages lint/compile/test/coverage: passed.
- History Event go-no-go with intake + generate-output: `go`.

## Known limitations

- CLI does not execute an AI renderer.
- Model-assisted output validation starts after a rendered file is supplied at the expected output path.
- Inferred values are detected deterministically when declared as forbidden unconfirmed terms or when they contradict confirmed-state validation rules.
