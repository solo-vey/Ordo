# M79.1 — Template Registry, schema and consistency gate

Implemented a generic Template Registry and a fail-closed consistency gate.

Deliverables:
- `cli/ordo/schemas/template_registry.schema.yaml`
- `validate_template_registry()`
- `ordo template registry-check`
- example registry for `qa.package`
- developer documentation and book reference
- regression tests for duplicates, stale checksum, metadata mismatch and multiple active versions
