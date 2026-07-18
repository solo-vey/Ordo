# Prompt Registry Smoke Test Plan — History Event Factory

Status: `M65.1 planned-smoke-test`

## Goal

Verify that prompt registry adoption is discoverable, safe, and connected to the current package model.

## Smoke test cases

### SMOKE-PR-01 — Quick start discoverability

Input: package README.

Expected:

- README points to `prompts/hp.package.quick_start.v1.md`;
- quick start prompt points to Runtime Mode entry;
- quick start prompt does not bypass CLI evidence rules.

### SMOKE-PR-02 — Prompt refs resolve

Input: source YAML after adoption patch.

Expected:

- every `prompt_refs[*].prompt_id` exists in `prompt_registry.prompts[*].prompt_id`;
- no orphan node prompt ref exists.

### SMOKE-PR-03 — Node ids exist

Input: source YAML after adoption patch.

Expected:

- `N_PATH_SELECT`, `N_SOURCE_FIELD`, `N_VALUE_SEMANTICS`, `N_DISPLAY_NAME_UK`, `N_DISPLAY_NAME_EN` are existing nodes;
- future APF ids are not referenced directly unless compatibility aliases are declared.

### SMOKE-PR-04 — Authority safety

Input: all prompt files.

Expected prompt files do not contain unsupported authority claims:

```text
ignore gate
skip validation
mark approved
write state directly
CLI validation passed
read compiled/program.ir.json directly
```

### SMOKE-PR-05 — Manifest coverage

Input: manifest/checksum file.

Expected:

- every prompt file appears in prompt manifest;
- required prompt files have checksums;
- deleted prompt files are not listed.

## Smoke readiness

The prompt adoption patch can be accepted only when hard smoke tests pass.
