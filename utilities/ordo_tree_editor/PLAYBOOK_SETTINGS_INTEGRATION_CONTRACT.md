# Ordo Editor — Playbook Settings Integration Contract

## Purpose

`Playbook Settings` is a read-only view of effective program-level configuration.
The Editor must not hard-code the meaning of language-level enum values in UI code.

## Sources of truth

1. Current values: loaded Ordo source (`program.ordo.yaml`).
2. Allowed/common values and English meanings: bundled language registry Markdown under:
   `verification/toolkit/language/registry/`.
3. The Editor discovers table rows dynamically from registry documents.

## Language-package assembly rule

When a newer language/tooling package is assembled into the Editor:

- copy the current language registry snapshot;
- preserve registry headings matching the source attribute name when possible;
- add new enum/convention values to registry tables rather than Editor JS;
- do not remove a value from the Editor by editing UI code;
- if a setting has no declared alternatives, the UI shows the current value and states that no enumerated alternatives are declared.

## Supported settings roots

The current Editor inspects program-level settings roots such as `ordo`, `interaction_model`,
`process_rail`, `conversation_semantics`, `hybrid_execution`, `execution_trace`,
`startup_package_profile`, `runtime_capabilities`, and related program-policy roots when present.

The view is inspection-only and must not mutate source semantics.


## R3 full catalog rule

The Editor MUST derive the settings inventory from bundled language schemas and registries, then overlay values from the loaded playbook. A language-defined setting remains visible even when the playbook does not declare it; its UI state is `Not specified`.

## AI assistant rule

The settings assistant is read-only. It may analyze current settings and propose YAML text, but MUST NOT mutate the loaded source, state, semantic plan, or package. Proposed YAML is always a user-applied artifact.
