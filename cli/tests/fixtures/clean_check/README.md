# Clean-check fixture packages

These packages are intentionally small real Ordo package fixtures used by M68.1
to test `ordo clean-check` without mutating applied packages under `packages/`.
Each fixture contains an `ordo.yml` when the scenario allows it and a source YAML
surface tailored to one clean-check behavior.

The fixtures are copied to temporary directories by the test suite before running
CLI commands so generated reports do not dirty the repository fixtures.
