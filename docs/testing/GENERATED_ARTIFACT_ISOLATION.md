# Generated Artifact Isolation

Source workspaces and generated outputs are separate.

## Source rules

- Package `compiled/`, `reports/`, `runtime/`, and `generated_outputs/` roots may contain only approved placeholders or source templates.
- Workspace `reports/` may contain only canonical historical records listed in `reports/CANONICAL_REPORTS_MANIFEST.yaml`.
- Unmanifested files under workspace `reports/` fail the strict isolation gate.
- Canonical report checksums must match the manifest.

## Generated roots

- Package outputs: `.ordo-generated/packages/<package_id>/`
- Workspace execution/report outputs: `.ordo-generated/workspace-reports/`

Generated artifacts enter release packages only through an explicit release manifest. Relocated report provenance is preserved in `manifests/GENERATED_REPORT_RELOCATION_MANIFEST.json`.

Run:

```bash
python tools/check_generated_artifact_isolation.py
```
