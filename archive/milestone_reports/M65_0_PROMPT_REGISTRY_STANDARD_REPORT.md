# M65.0 — Prompt Registry Standard Report

Status: `accepted-docs-schema-convention`

## Scope

M65.0 promotes the Node-Level Prompt Registry and Prompt References improvement from backlog into a language/package standard design milestone.

The milestone defines:

- `prompt_registry` top-level source convention;
- `prompt_refs` references from nodes and other package elements;
- prompt types, audiences, lifecycle, visibility, state-change policy, and validation policy;
- prompt registry consistency gate shape;
- manifest integration convention;
- trace awareness convention;
- schema conventions and example source YAML;
- clear authority boundary: helper prompts support but do not override process model.

## Added files

- `language/PROMPT_REGISTRY.md`
- `language/registry/PROMPT_REGISTRY_VALUES.md`
- `language/schemas/prompt_registry_schema.yaml`
- `language/schemas/prompt_ref_schema.yaml`
- `language/examples/source/prompt_registry_example.ordo.yaml`
- `language/spec/19_PROMPT_REGISTRY_MODEL.md`
- `docs/design_decisions/DD-ORDO-M65-001_PROMPT_REGISTRY_STANDARD.md`
- `language/improvement_intake/m65_0/APF_NODE_LEVEL_PROMPT_REGISTRY_IMPROVEMENT_SOURCE.md`
- `language/improvement_intake/m65_0/M65_0_PROMPT_REGISTRY_STANDARD_REPORT.md`
- `language/improvement_intake/m65_0/M65_0_PROMPT_REGISTRY_STANDARD_REPORT.json`
- `language/improvement_intake/m65_0/M65_0_VALIDATION_REPORT.json`

## Changed files

- `language/README.md`
- `language/CHANGELOG.md`
- `language/CURRENT_VERSION.md`
- `language/VALIDATION_REPORT.json`
- `language/schemas/node_schema.yaml`
- `FUTURE_BACKLOG.md`
- `STABLE_PACKAGE_INDEX.md`
- `CHANGELOG.md`

## Non-changes

- no runtime core changes;
- no compiler behavior changes;
- no CLI command changes;
- no opcode promotion;
- no deterministic natural-language classifier;
- no APF source YAML rewrite.

## Acceptance result

M65.0 is accepted as a documentation/schema/lint-profile design milestone.

Future work remains:

- CLI/linter enforcement for prompt registry consistency;
- concrete APF/History Event Factory prompt files and registry adoption;
- manifest checksum hardening;
- prompt-specific trace output in runtime/session reports.
