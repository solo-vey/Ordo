# Getting started with Ordo

1. Install the CLI in editable mode from the `cli/` directory.
2. Validate one of the current reference packages in `packages/`.
3. For an authoring scenario, use `packages/ordo_project_builder`.
4. For an execution scenario, use `packages/ordo_hybrid_executor`.

```bash
cd cli
python -m pip install -e .
ordo lint ../packages/ordo_project_builder
ordo compile ../packages/ordo_project_builder
ordo test ../packages/ordo_project_builder
ordo coverage ../packages/ordo_project_builder
ordo validate-state ../packages/ordo_project_builder --answers ../packages/ordo_project_builder/run_inputs/authoring_success.yaml
ordo next-step ../packages/ordo_project_builder --answers ../packages/ordo_project_builder/run_inputs/authoring_success.yaml
```

The CLI in this workspace is a helper layer: it validates, compiles, and
explains Process Rail state, but does not replace an AI Ordo Developer or AI
Ordo Executor.
