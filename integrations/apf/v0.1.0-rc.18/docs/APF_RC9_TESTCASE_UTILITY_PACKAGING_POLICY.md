# APF rc.9 — Testcase Utility Packaging Policy

## Utility path

```text
utilities/apf_real_module_testcase_generator/
```

## Required structure

```text
utilities/apf_real_module_testcase_generator/
  APF_REAL_MODULE_TESTCASE_GENERATOR_MANIFEST.json
  README.md
  schemas/
    testcase_target_manifest.schema.json
    model_confusion_scenario_catalog.schema.json
    expected_behavior_matrix.schema.json
    generated_testcase_plan.schema.json
  examples/
    minimal_testcase_target_manifest.yaml
    model_confusion_scenario_catalog.example.yaml
    expected_behavior_matrix.example.yaml
    generated_testcase_plan.example.yaml
```

## Boundary

The utility is an APF packaging/specification utility. It must not execute Ordo runtime, modify language package contents, or claim runtime test results.
