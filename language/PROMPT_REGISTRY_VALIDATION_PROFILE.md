# Prompt Registry Validation / Lint Profile

Status: `M71.2 updated convention / no runtime implementation`

## Purpose

This profile extends the M65 validation model with the stable semantic identity and versioning rules accepted in M71.1. It remains a review/lint contract and does not grant prompts navigation or state authority.

## Profile levels

| Profile | Intended use | Identity/lineage behavior |
|---|---|---|
| `light` | Draft migration and exploratory package work. | Legacy unversioned or node-coupled ids may be warnings; unresolved refs remain errors. |
| `standard` | Normal package acceptance and release-candidate packaging. | Semantic/versioned identity, family/version consistency, valid phases, and resolvable lineage are blocking. |
| `strict` | Published/release gate. | All standard checks plus stable-id immutability, deprecated refs, checksum drift, reverse-mapping drift, and trace readiness. |

## Controlled application phases

Only these values are valid for `prompt_refs[].use`:

```text
before_question
during_clarification
after_answer
before_confirmation
on_open_gap
on_gate_fail
before_artifact_generation
```

List order is normative when multiple prompts use the same phase.

## Required checks

| Check id | Category | Light | Standard | Strict | Intent |
|---|---|---|---|---|---|
| `prompt_registry_present` | structure | error | error | error | Registry exists when prompts are contract artifacts. |
| `prompt_registry_schema_valid` | structure | error | error | error | Registry follows the schema convention. |
| `prompt_ids_unique` | identity | error | error | error | IDs are unique. |
| `prompt_ids_semantic_and_node_independent` | identity | warning | error | error | IDs describe stable roles, not node positions. |
| `prompt_id_version_matches_version_field` | identity | warning | error | error | `.vN` equals `version: N`. |
| `prompt_family_matches_prompt_id` | identity | warning | error | error | Family equals ID without `.vN`. |
| `prompt_filename_semantic_and_node_independent` | file | warning | error | error | Filename is semantic and not prefixed by node id. |
| `supersedes_resolves_within_same_family` | lineage | warning | error | error | Superseded ID resolves in the same family. |
| `supersedes_version_is_lower` | lineage | warning | error | error | A prompt supersedes only a lower version. |
| `supersedes_lineage_acyclic` | lineage | warning | error | error | No lineage cycles. |
| `stable_prompt_id_immutable` | identity | info | warning | error | Published stable IDs are not reused for a different semantic contract. |
| `prompt_paths_exist` | file | error | error | error | Every declared file exists. |
| `required_prompts_present` | file | error | error | error | Required prompts exist. |
| `prompt_refs_resolve` | reference | error | error | error | Every ref resolves. |
| `prompt_ref_application_phase_valid` | application | warning | error | error | `use` is from the controlled vocabulary. |
| `prompt_ref_order_deterministic` | application | info | warning | error | Same-phase order is deterministic. |
| `node_prompt_refs_target_existing_nodes` | reference | warning | error | error | Node refs attach to real nodes. |
| `artifact_prompt_refs_target_existing_artifacts` | reference | warning | error | error | Artifact refs attach to real artifacts/templates. |
| `reverse_node_mapping_consistent` | reference | info | warning | error | Registry reverse mapping, if present, matches authoritative refs. |
| `prompt_manifest_coverage` | traceability | warning | error | error | Prompt files are covered by a manifest. |
| `prompt_manifest_checksum_valid` | traceability | info | warning | error | Checksums match exact file contents. |
| `prompt_authority_safe` | authority | warning | error | error | Prompt cannot bypass gates, alter routing, or silently mutate confirmed state. |
| `state_change_policy_consistent` | authority | warning | error | error | Declared state authority matches prompt content. |
| `stale_prompt_refs` | lineage | info | warning | error | Stable refs do not point to deprecated prompts without rationale. |
| `trace_prompt_refs_recordable` | traceability | info | info | warning | Runtime evidence can record id, phase, and checksum when supported. |

## Migration handling

Legacy node-coupled or unversioned IDs are migration findings, not a reason to create a second registry. Under `light` they may remain warnings. Under `standard` and `strict`, newly accepted or migrated package registries must use stable semantic IDs.

## Authority rule

Executable decision model remains authoritative for navigation. Prompts govern only local behavior inside an already selected node or artifact phase. Natural-language authority review may be manual or heuristic; this profile does not claim deterministic classification.

## Recommended gate

```yaml
PROMPT_REGISTRY_VALIDATION_GATE:
  type: hard_with_warning_support
  profile: standard
  checks:
    - prompt_registry_schema_valid
    - prompt_ids_unique
    - prompt_ids_semantic_and_node_independent
    - prompt_id_version_matches_version_field
    - prompt_family_matches_prompt_id
    - supersedes_resolves_within_same_family
    - supersedes_version_is_lower
    - supersedes_lineage_acyclic
    - prompt_paths_exist
    - prompt_refs_resolve
    - prompt_ref_application_phase_valid
    - prompt_manifest_coverage
    - prompt_authority_safe
```

## M71.2 boundary

M71.2 updates schemas, validation profile, examples, and review tests only. It does not migrate package IDs or filenames and does not change runtime, compiler, opcodes, compiled IR, or navigation.
