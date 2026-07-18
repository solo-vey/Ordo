# M65.3 — Prompt Registry Validation / Lint Profile Design Report

Status: `accepted-design / passed-docs-schema-validation`

## Scope

M65.3 formalizes how `prompt_registry` and `prompt_refs` should be validated before package acceptance.

## Added files

- `language/PROMPT_REGISTRY_VALIDATION_PROFILE.md`
- `language/schemas/prompt_registry_validation_profile_schema.yaml`
- `language/examples/source/prompt_registry_validation_profile_example.ordo.yaml`
- `language/spec/20_PROMPT_REGISTRY_VALIDATION_MODEL.md`
- `docs/design_decisions/DD-ORDO-M65-004_PROMPT_REGISTRY_VALIDATION_LINT_PROFILE.md`

## Changed files

- `language/registry/PROMPT_REGISTRY_VALUES.md`
- `language/README.md`
- `language/CHANGELOG.md`
- `README.md`
- `CHANGELOG.md`
- `FUTURE_BACKLOG.md`
- `STABLE_PACKAGE_INDEX.md`

## Accepted design

M65.3 defines:

- prompt registry validation profiles: `light`, `standard`, `strict`;
- lint severity model: `error`, `warning`, `info`;
- approval decisions: `approved`, `approved_with_warnings`, `blocked`, `not_applicable`;
- required checks for registry presence, schema validity, prompt ids, paths, refs, target resolution, manifest coverage, quick-start discoverability, authority-safe text, and state-change policy consistency;
- warning checks for unused prompt files, stale refs, duplicate content, and trace recordability.

## Non-changes

- no runtime core change;
- no compiler behavior change;
- no CLI command change;
- no opcode promotion;
- no deterministic prompt authority classifier;
- no compiled IR regeneration;
- no additional History Event Factory prompt file migration beyond M65.2.

## Acceptance result

M65.3 is accepted as a docs/schema/lint-profile design milestone.
