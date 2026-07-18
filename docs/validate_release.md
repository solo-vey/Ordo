# M6: Package Quality Gates & Release Validation

`ordo validate-release` is the M6 quality gate for Ordo packages.

It is intended to be run before a package is published, handed off, or committed as a ready artifact.

```bash
ordo validate-release packages/ordo_project_builder --skip-runtime
```

The command performs the following checks:

1. required package files exist;
2. `ordo.yml` has package metadata;
3. `lint` passes;
4. Source compiles into Semantic JSON IR;
5. static tests pass;
6. coverage is generated;
7. runtime helper-runner is executed when `run_inputs/answers_success.yaml` exists;
8. guided intake is executed when `run_inputs/intake_success.yaml` exists;
9. release archive is created;
10. `reports/release_validation_report.json` is written.

For `strict` packages, missing gate/assertion coverage is a release-blocking error. For `standard` packages it is currently a warning.

M6 is not a full AI runtime. It validates package readiness around the Ordo source, IR, tests, coverage, and available deterministic runtime checks.
