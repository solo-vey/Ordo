# Stable Prompt Identity and Versioning Convention

Status: `M71.1 accepted convention`

M71.1 extends the existing M65 Prompt Registry without replacing it.

## Canonical rule

```text
prompt_id != node_id
```

Use semantic, versioned identifiers:

```text
hp.delta_intake.single_field.v1
hp.localization.bilingual_texts.v1
hp.qa.after_contract_only.v1
```

Avoid tree-coupled identifiers:

```text
N_SOURCE_FIELD_external_fact_intake_helper
B1_N2B_delta_prompt
```

## Required identity fields

```yaml
prompt_id: hp.delta_intake.single_field.v1
prompt_family: hp.delta_intake.single_field
version: 1
supersedes: null
```

`prompt_id` is immutable. A semantic breaking change creates a new major version and an explicit `supersedes` link.

## Compatibility rule

Node rename/split/merge updates `prompt_refs`; it does not rename the prompt when semantic purpose is unchanged.

## Source of truth

Node/artifact/gate `prompt_refs` are authoritative attachments. Registry-side reverse mappings are derived metadata only.

## Content revisions

Non-breaking text edits do not require a new major ID. Exact content remains auditable through manifest SHA-256.

## Application ordering

Use a controlled `use` vocabulary. When multiple refs share a phase, list order is normative.

## Migration boundary

M71.1 defines the convention only. Package migration is deferred to the later M71 implementation step.
