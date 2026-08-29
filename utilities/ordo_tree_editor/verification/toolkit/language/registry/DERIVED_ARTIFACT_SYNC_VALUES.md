# Derived Artifact Sync Registry Values

Status: M67.0 registry convention.

## Profiles

- `light`
- `standard`
- `strict`

## Artifact roles

- `package_source`
- `prompt_source`
- `startup_profile`
- `validation_profile`
- `manifest`
- `lockfile`
- `compiled_ir`
- `rendered_document`
- `graph_export`
- `report`
- `evidence_pack`

## Derivation methods

- `manual_authoring`
- `compiler_output`
- `renderer_output`
- `checksum_manifest`
- `graph_renderer_output`
- `validation_report`
- `archive_packaging`
- `manual_or_tool_verified`

## Freshness policies

- `must_exist`
- `must_match_hash`
- `manual_or_tool_verified`
- `regenerate_required`
- `not_applicable`

## Stale actions

- `block_release`
- `open_delta_backlog`
- `warn_only`
- `ignore_for_draft`

## Delta backlog areas

- `derived_artifact_sync`
- `prompt_registry_packaging`
- `startup_profile_packaging`
- `manifest_coverage`
- `compiled_ir_regeneration`
- `graph_export_regeneration`
- `documentation_sync`
- `validation_profile_followup`
