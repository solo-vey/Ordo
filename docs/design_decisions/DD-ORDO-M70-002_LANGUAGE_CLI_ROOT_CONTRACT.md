# DD-ORDO-M70-002 — Language / CLI Root Contract

## Decision
Use a dedicated read-only `root_contract` treatment for `language/` and `cli/` instead of manufacturing package-level `ordo.yml` manifests.

## Consequences
Both roots become truthfully release-blocking. Package clean-check semantics stay unchanged, and applied packages remain delegated.
