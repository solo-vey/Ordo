# SELF-CHECK REPAIR 2 — Prompt Registry documentation and examples alignment

Status: `repaired_passed`

## Scope

Aligned active language-level Prompt Registry and startup documentation/examples with the M71 semantic prompt identity convention.

## Updated files

- `language/PROMPT_REGISTRY.md`
- `language/PACKAGE_STARTUP_STANDARD.md`
- `language/STARTUP_PACKAGE_PROFILE.md`
- `language/STARTUP_PROFILE_VALIDATION_PROFILE.md`
- `language/registry/STARTUP_PACKAGE_PROFILE_VALUES.md`
- `language/spec/19_PROMPT_REGISTRY_MODEL.md`
- `language/examples/source/prompt_registry_example.ordo.yaml`
- `language/examples/source/startup_package_profile_example.ordo.yaml`

## Replacements

Legacy examples such as `quick_start_prompt`, `runtime_start_prompt`, `ROOT_N1_source_type_clarification`, and `B5_N3_comparison_rule_helper` were replaced with semantic versioned IDs such as:

- `hp.package.quick_start.v1`
- `hp.runtime.start.v1`
- `hp.source_type.clarification.v1`
- `hp.normalization.value_comparison.v1`

Registry entries now demonstrate `prompt_family`, integer `version`, and `supersedes`.
Prompt references remain references only and do not duplicate registry identity metadata.

## Validation

- example YAML parse: passed
- M71.2 schema/profile tests: 6 passed
- active language docs legacy prompt-id declarations: none found
- strict repository gate with fail-on-warning: passed

## Non-changes

No package logic, navigation, runtime, compiler, opcode, or applied package prompt registry was changed.
