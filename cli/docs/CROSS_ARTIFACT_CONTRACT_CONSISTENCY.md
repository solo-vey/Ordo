# Cross-artifact contract consistency

`tools/validate_cross_artifact_contract_consistency.py` is a release-facing
semantic check for playbook packages. It is deliberately separate from graph
linting and compilation: those checks prove that the playbook is structurally
valid, while this check proves that external contract artifacts still describe
the same live state model.

For each package with applicable surfaces, the validator compares:

- `state.schema` in the playbook source;
- external gate specifications in `gates/`;
- Markdown output templates and `*BINDINGS.yaml` files in `output_templates/`;
- an optional variable registry in `registry/`.

The blocking findings are:

- `CAC-001` — a binding reads an undeclared state root;
- `CAC-002` — a registry path reads an undeclared state root;
- `CAC-003` — a template placeholder has no binding;
- `CAC-004` — a gate requires a state object absent from `state.schema`;
- `CAC-005` — a repeated gate semantic domain has no live contract support.

Packages without these optional surfaces are reported as `SKIPPED`, not as
failures. This lets the repository gate all playbook packages while keeping
the check applicable only where the package declares the relevant artifacts.

Run one package:

```bash
python tools/validate_cross_artifact_contract_consistency.py \
  --root packages/my_playbook \
  --json-out reports/cross_artifact_contract_consistency.json
```

Run repository discovery (the CI entry point):

```bash
python tools/validate_cross_artifact_contract_consistency.py \
  --repo-root . \
  --json-out reports/ci/cross_artifact_contract_consistency.json
```

The check runs after YAML/schema and package lint validation and before the
delivery/release gate. Its JSON report is retained as CI evidence.
