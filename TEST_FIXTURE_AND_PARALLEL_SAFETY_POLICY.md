# Test Fixture Mutation and Parallel Execution Safety

## Negative fixture mutation

Every negative test that creates a defect using textual replacement, regex substitution, patching or structured mutation must assert that the input actually changed before invoking the system under test. A mutation without such proof is the `SILENT_FIXTURE_NOOP` anti-pattern.

## Execution classes

Test files are classified as `parallel_safe`, `workspace_reading`, `workspace_mutating`, or `performance_sensitive`. The canonical classification is `manifests/TEST_EXECUTION_CLASSIFICATION.json`.

`workspace_mutating` tests run in one serial batch after all parallel batches. `performance_sensitive` tests run in that same quiet serial phase. Parallel tests may write only under private temporary directories.

## Determinism gate

Release-gate changes must pass repeated scheduler-contract tests and at least three dry partition plans with identical serial membership. The independent end-to-end external run remains part of BL-ORDO-026.
