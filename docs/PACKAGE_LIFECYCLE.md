# Package Lifecycle Contract

Release-bound packages may enable a strict `maintenance_lifecycle` block in
`ordo.yml`. It makes maintenance reproducible and prevents a release from
silently losing its source baseline, change history, or regression evidence.

```yaml
maintenance_lifecycle:
  version: "1.0"
  mode: strict
  required_assets:
    - README.md
    - tests/test_cases.yaml
    - maintenance/apply_patch.py
  checkpoint: {path: lifecycle/checkpoint.json}
  patch:
    path: maintenance/apply_patch.py
    baseline_source_sha256: <canonical-source-sha256>
    idempotent: true
  previous_release: {path: lifecycle/previous_release.json}
  regression: {path: lifecycle/canonical_regression_report.json}
  release_evidence: {path: lifecycle/release_evidence.json}
  runtime_excluded_paths: [maintenance, tools]
```

The patch script must contain both `LIFECYCLE_PATCH_IDEMPOTENT = True` and a
`BASELINE_SOURCE_SHA256` assertion. The immutable checkpoint and patch must
name the same pre-change source digest. Before applying a patch, compare the
current source with that baseline; after a successful change, release evidence
instead binds to the new canonical source digest.

Use the commands below before publishing:

```text
ordo validate-lifecycle PACKAGE_PATH
ordo validate-lifecycle PACKAGE_PATH --verify-baseline
ordo validate-release PACKAGE_PATH
ordo validate-unpacked-release RELEASE.zip
```

`validate-unpacked-release` extracts the ZIP in an isolated temporary location
and repeats lifecycle validation. It rejects unsafe archive member paths and
archives that contain zero or multiple package manifests.
