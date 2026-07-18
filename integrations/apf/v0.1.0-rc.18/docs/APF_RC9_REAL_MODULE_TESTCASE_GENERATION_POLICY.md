# APF rc.9 — Real-module Testcase Generation Policy

## Purpose

Real-module testcase generation planning makes an APF-created package testable at the specification level. The package must declare the module/package under test, the critical gates, expected terminal outputs, risk scenarios, and expected APF behavior.

## In scope

- Generate testcase specifications.
- Generate testcase plans.
- Generate expected behavior matrices.
- Generate model-confusion scenario coverage.
- Check whether the APF package contains enough metadata for future testing.

## Out of scope

- Running Ordo compiler/runtime tests.
- Implementing Ordo CLI commands.
- Modifying the Ordo language package.
- Claiming runtime test success without external evidence.

## Required gates

- `REAL_MODULE_TESTCASE_GENERATION_PLANNING_GATE`
- `REAL_MODULE_TESTCASE_UTILITY_PACKAGING_GATE`

## Required artifacts

- `tests/REAL_MODULE_TESTCASE_TARGET_MANIFEST.yaml`
- `tests/MODEL_CONFUSION_SCENARIO_CATALOG.yaml`
- `tests/EXPECTED_BEHAVIOR_MATRIX.yaml`
- `reports/APF_REAL_MODULE_TESTCASE_GENERATION_PLAN_REPORT.json`
- `utilities/apf_real_module_testcase_generator/APF_REAL_MODULE_TESTCASE_GENERATOR_MANIFEST.json`
