# APF rc.9 Confirmation Register

## APF-RC9-01

Decision: APF rc.9 includes both testcase generation planning gate and APF-level testcase generator utility packaging gate.

Status: confirmed

Scope: APF package/playbook creation process only.


## APF-RC9-02

Decision: tests/REAL_MODULE_TESTCASE_TARGET_MANIFEST.yaml is required for packages that claim real-module testcase generation planning support.

Status: confirmed

Scope: APF package/playbook creation process only.


## APF-RC9-03

Decision: tests/MODEL_CONFUSION_SCENARIO_CATALOG.yaml is the standard catalog for negative/confusion/boundary/false-green testcase planning.

Status: confirmed

Scope: APF package/playbook creation process only.


## APF-RC9-04

Decision: tests/EXPECTED_BEHAVIOR_MATRIX.yaml is required to map scenarios to expected APF behavior, gates, expected statuses, and forbidden statuses.

Status: confirmed

Scope: APF package/playbook creation process only.


## APF-RC9-05

Decision: reports/APF_REAL_MODULE_TESTCASE_GENERATION_PLAN_REPORT.json is required to evaluate readiness for real-module testcase generation planning.

Status: confirmed

Scope: APF package/playbook creation process only.


## APF-RC9-06

Decision: utilities/apf_real_module_testcase_generator/ is the standard APF utility folder for testcase specification generation, with manifest, schemas, and examples.

Status: confirmed

Scope: APF package/playbook creation process only.


## APF-RC9-07

Decision: REAL_MODULE_TESTCASE_GENERATION_PLANNING_GATE and REAL_MODULE_TESTCASE_UTILITY_PACKAGING_GATE are placed after rc.8 confirmation gates and before EXTERNAL_CHECK_EVIDENCE_GATE/PACKAGE_COMPOSITION_GATE.

Status: confirmed

Scope: APF package/playbook creation process only.
