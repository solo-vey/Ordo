# APF Real-module Testcase Generator

This utility folder defines the APF-level packaging contract for generating testcase specifications and plans for real APF-created modules.

It is **not** an Ordo runtime test runner.

## Inputs

- `tests/REAL_MODULE_TESTCASE_TARGET_MANIFEST.yaml`
- `tests/MODEL_CONFUSION_SCENARIO_CATALOG.yaml`
- `tests/EXPECTED_BEHAVIOR_MATRIX.yaml`

## Outputs

- `tests/GENERATED_TESTCASE_PLAN.yaml`
- `reports/APF_REAL_MODULE_TESTCASE_GENERATION_PLAN_REPORT.json`

## Forbidden actions

- Run Ordo compiler.
- Execute Ordo runtime.
- Modify Ordo language package.
- Claim runtime tests passed without external evidence.
