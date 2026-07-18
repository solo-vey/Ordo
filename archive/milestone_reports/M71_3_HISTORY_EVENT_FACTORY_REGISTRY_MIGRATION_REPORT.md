# M71.3 — History Event Factory Registry Migration

Status: `implemented / passed-validation`

## Scope

Migrated the existing History Event Factory Prompt Registry from node-coupled and unversioned prompt identifiers to stable semantic versioned identifiers. This is a migration of the M65 implementation, not a second registry.

## Result

- 13 existing prompts migrated to semantic `prompt_id` values.
- Every entry now carries `prompt_family`, integer `version`, and `supersedes`.
- Prompt filenames are semantic and independent of node ids.
- All node, gate, artifact, output, startup, documentation, and manifest references were updated.
- `PROMPT_MANIFEST.json` was rebuilt with current SHA-256 checksums and legacy compatibility mappings.
- Application phase aliases were normalized to the M71.2 controlled vocabulary.
- Business navigation, gates, state model, confirmations, and output contracts were unchanged.

## Compatibility

Legacy IDs are retained only in `PROMPT_ID_MIGRATION_MAP.*` and manifest compatibility metadata. Runtime/source refs use only stable IDs.

## Validation

- M71.3 + M71.2 tests: 11 passed.
- Bounded registry/repo regression: 19 passed.
- Package `clean-check --profile standard`: passed, 0 warnings, 0 errors.
- 22 prompt refs resolve.
- 13 manifest checksums match.
- Business-contract structural diff: passed for all core sections.
