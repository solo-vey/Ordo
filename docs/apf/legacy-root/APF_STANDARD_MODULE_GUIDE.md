# APF Standard Module Guide — rc.1

`ordo.applied_project_factory` is included as a release-candidate standard applied module.

- Module id: `ordo.applied_project_factory`
- Version: `0.1.0-rc.1`
- Lifecycle: `release-candidate`
- Path: `packages/ordo_applied_project_factory/`
- Parent line: `Ordo v0.12 / M62 line closure`

## How to validate

From the language package root:

```bash
PYTHONPATH=cli:. python -m cli.ordo.cli lint packages/ordo_applied_project_factory
PYTHONPATH=cli:. python -m cli.ordo.cli compile packages/ordo_applied_project_factory
PYTHONPATH=cli:. python -m cli.ordo.cli test packages/ordo_applied_project_factory
PYTHONPATH=cli:. python -m cli.ordo.cli coverage packages/ordo_applied_project_factory
PYTHONPATH=cli:. python -m cli.ordo.cli validate-state packages/ordo_applied_project_factory --state packages/ordo_applied_project_factory/run_inputs/rc1_full_validation_state.yaml
PYTHONPATH=cli:. python -m cli.ordo.cli next-step packages/ordo_applied_project_factory --state packages/ordo_applied_project_factory/run_inputs/rc1_full_validation_state.yaml
PYTHONPATH=cli:. python -m cli.ordo.cli validate-output packages/ordo_applied_project_factory
PYTHONPATH=cli:. python -m cli.ordo.cli validate-artifacts packages/ordo_applied_project_factory --state packages/ordo_applied_project_factory/run_inputs/rc1_full_validation_state.yaml
PYTHONPATH=cli:. python -m cli.ordo.cli consistency packages/ordo_applied_project_factory --state packages/ordo_applied_project_factory/run_inputs/rc1_full_validation_state.yaml
PYTHONPATH=cli:. python -m cli.ordo.cli go-no-go packages/ordo_applied_project_factory --state packages/ordo_applied_project_factory/run_inputs/rc1_full_validation_state.yaml
```

`validate-factory-output` is APF-local / optional in this release-candidate line.

## Known limitations

- `consistency` may return `passed_with_warnings`; warnings are non-blocking but must remain visible.
- `FLOW.JOIN` and `SHARED.TAIL.REFERENCE` remain future IR candidates.
- APF patterns are documented as applied-module patterns, not mandatory core opcodes.
