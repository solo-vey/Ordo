# APF rc.9 Confirmed Closure — Accepted Baseline

## Status

- module_id: `ordo.applied_project_factory`
- current_version: `v0.1.0-rc.9-confirmed-closure`
- source_version: `v0.1.0-rc.9-real-module-testcase-generation`
- status: `accepted-baseline / ready-for-next-apf-patch`
- blocking_issues: `0`
- scope_boundary: APF package/playbook creation process only; no Ordo language package changes.

## Confirmed decisions

- APF-RC9-01 — planning gate + utility packaging gate.
- APF-RC9-02 — testcase target manifest.
- APF-RC9-03 — model-confusion scenario catalog.
- APF-RC9-04 — expected behavior matrix.
- APF-RC9-05 — coverage planning report.
- APF-RC9-06 — utility manifest and packaging standard.
- APF-RC9-07 — gate placement in final tail.

## Accepted baseline meaning

APF rc.9 is accepted as the baseline for real-module testcase generation planning. The package now treats testcase planning artifacts and the APF-level testcase specification utility as first-class package contents.

This closure does not implement Ordo compiler/runtime testing and does not add language package changes.

## Stable rc.9 artifacts

- `tests/REAL_MODULE_TESTCASE_TARGET_MANIFEST.yaml`
- `tests/MODEL_CONFUSION_SCENARIO_CATALOG.yaml`
- `tests/EXPECTED_BEHAVIOR_MATRIX.yaml`
- `tests/GENERATED_TESTCASE_PLAN.yaml`
- `utilities/apf_real_module_testcase_generator/APF_REAL_MODULE_TESTCASE_GENERATOR_MANIFEST.json`
- `reports/APF_REAL_MODULE_TESTCASE_GENERATION_PLAN_REPORT.json`

## Accepted final tail fragment

```text
APF_PACKAGE_CREATION_HARDENING_GATE
→ NODE_CHANGE_IMPACT_REVIEW_GATE
→ GATE_ORDER_CONFIRMATION_GATE
→ PROCESS_RAIL_CHANGE_CONFIRMATION_GATE
→ PACKAGE_PROFILE_CHANGE_CONFIRMATION_GATE
→ REAL_MODULE_TESTCASE_GENERATION_PLANNING_GATE
→ REAL_MODULE_TESTCASE_UTILITY_PACKAGING_GATE
→ EXTERNAL_CHECK_EVIDENCE_GATE
→ PACKAGE_COMPOSITION_GATE
→ FINAL_ARCHIVE_ASSEMBLY
```
