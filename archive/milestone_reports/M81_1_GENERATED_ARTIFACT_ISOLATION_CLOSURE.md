# M81.1 Generated Artifact Isolation Closure

Status: PASS

- Package-level generated outputs remain externalized under `.ordo-generated/packages/`.
- Workspace-level generated reports are externalized under `.ordo-generated/workspace-reports/`.
- `reports/` now contains only canonical historical records declared in `reports/CANONICAL_REPORTS_MANIFEST.yaml`.
- 701 generated/runtime/report files were relocated with checksum provenance in `manifests/GENERATED_REPORT_RELOCATION_MANIFEST.json`.
- Strict source-tree isolation gate validates both package roots and workspace reports.
- Release inclusion remains explicit-manifest-only.
- Targeted reconciliation and isolation tests: 5/5 PASS.
- Clean-gate workflow tests: 13/13 PASS.
- BL-ORDO-012: closed.
