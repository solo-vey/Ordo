# Derived Artifact Sync Standard

Status: M67.0 accepted draft standard.

Defines how an Ordo package declares source-of-truth files and derived artifacts that must stay synchronized with them. This is a documentation/schema/package-consistency convention only.

## Purpose

A package may contain source YAML, prompts, generated manifests, lockfiles, compiled runtime IR, rendered documents, graph exports, reports, and evidence packs. The package should make provenance and freshness explicit.

## Canonical block

```yaml
artifact_sync:
  sync_id: history_event_factory_artifact_sync
  profile: standard
  source_of_truth:
    - path: packages/history_event_guided_intake/source/program.ordo.yaml
      role: package_source
  derived_artifacts:
    - artifact_id: prompt_manifest
      path: packages/history_event_guided_intake/PROMPT_MANIFEST.json
      derived_from:
        - packages/history_event_guided_intake/prompts/
      derivation_method: checksum_manifest
      freshness_policy: must_match_hash
      stale_action: block_release
```

## Profiles

- `light`: advisory only.
- `standard`: reusable packages and standard applied modules.
- `strict`: release candidates and CI-backed packages.

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

## Authority boundary

Derived artifacts do not override source-of-truth unless an explicit package contract says otherwise.

## Non-goals

No runtime, compiler, CLI, IR, opcode, or automatic regeneration changes are introduced in M67.0.
