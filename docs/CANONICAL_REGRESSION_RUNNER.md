# Canonical Regression Runner

`ordo regression PACKAGE_PATH` executes the source-bound structural validation
contour: canonical source identity, lint, dynamic graph discovery, compilation,
static test expectations, and coverage. Its report always includes the
canonical source's verified path, size, modification metadata, and SHA-256.

Packages can opt in to strict structural regression by adding:

```yaml
regression_contract:
  version: "1.0"
  mode: strict
  decision_rule_coverage: required
  negative_assertions:
    - kind: vertex
      id: N_REMOVED_LEGACY_STEP
    - kind: artifact
      id: A_REMOVED_LEGACY_REPORT
```

With `decision_rule_coverage: required`, every active node and executable gate
discovered from the current graph must be referenced by a test expectation.
`graph_contract.deleted_ids` is also tested as an implicit negative assertion.
The runner never relies on a manually maintained vertex inventory.
