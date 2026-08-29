# Stable Prompt Identity and Versioning Model

Status: `M71.1 accepted language convention`

## 1. Identity principle

A prompt identifier represents a stable semantic role, not a node location.

```text
prompt_id != node_id
prompt filename != node filename
```

Node rename, split, merge, or relocation must not force a prompt identity change when the prompt's semantic role remains unchanged.

## 2. Canonical identity shape

```text
<namespace>.<semantic_role>.v<major>
```

Example:

```text
hp.delta_intake.single_field.v1
```

Rules:

- lowercase ASCII;
- dot-separated semantic segments;
- final segment is `v<positive integer>`;
- node IDs, gate IDs, branch IDs, and transient tree coordinates are forbidden as identity segments;
- identifiers are immutable after publication.

## 3. Prompt family

Each prompt belongs to a stable family without the major-version suffix.

```yaml
prompt_id: hp.delta_intake.single_field.v1
prompt_family: hp.delta_intake.single_field
version: 1
```

`prompt_family` groups compatible lineage; `prompt_id` identifies one immutable major semantic contract.

## 4. Versioning rules

Create a new major prompt version when any of the following changes:

- semantic purpose;
- authority boundary;
- required/forbidden behavior;
- expected confirmation contract;
- application phase compatibility;
- open-gap behavior.

Do not create a new major version for:

- typo fixes;
- wording clarification that does not change obligations;
- formatting-only changes;
- examples that do not alter the contract.

Content changes within one major version remain traceable through the prompt-file checksum in `PROMPT_MANIFEST.json`.

## 5. Lineage

```yaml
prompt_id: hp.delta_intake.single_field.v2
prompt_family: hp.delta_intake.single_field
version: 2
supersedes: hp.delta_intake.single_field.v1
```

Rules:

- `supersedes` is optional for the first version;
- when present, it must resolve to an existing prompt in the same family;
- a stable prompt may not supersede itself;
- deprecation does not delete the old identifier;
- references migrate explicitly.

## 6. Lifecycle

Allowed lifecycle values remain:

```text
draft
stable
deprecated
```

Additional rules:

- published stable IDs are immutable;
- deprecated IDs remain resolvable for audit and replay;
- new refs must not target deprecated IDs unless an explicit compatibility waiver exists;
- removal from a package requires a migration/evidence record.

## 7. Attachment authority

`prompt_refs` on nodes/artifacts/gates are the authoritative attachment source.

```yaml
prompt_refs:
  - prompt_id: hp.delta_intake.single_field.v1
    use: before_question
```

Registry-side `current_nodes`, if present, is derived or a validated mirror only. It is never the runtime source of truth.

## 8. Application phase

`use` values must come from a controlled vocabulary:

```text
before_question
during_clarification
after_answer
before_confirmation
on_open_gap
on_gate_fail
before_artifact_generation
```

List order is normative when several prompts share the same application phase.

## 9. Authority boundary

A prompt may control only local behavior inside the current executable step. It may not:

- create a transition;
- change `next_node`;
- skip a required node;
- bypass a gate;
- mutate confirmed state without the executable model.

Priority remains:

```text
executable decision model -> navigation/state authority
prompt -> local interaction guidance only
```

## 10. Descriptive metadata

Fields such as `semantic_roles`, `current_nodes`, and `applies_when` are descriptive metadata unless explicitly compiled by a future language feature. M71.1 does not make them executable.

## 11. Trace identity

Trace evidence should record:

```json
{
  "prompt_id": "hp.delta_intake.single_field.v1",
  "use": "before_question",
  "sha256": "..."
}
```

The trace records prompt identity and content checksum, not hidden reasoning or prompt text.

## 12. Non-goals

M71.1 does not:

- migrate package prompt IDs;
- rename prompt files;
- change runtime navigation;
- add opcodes;
- introduce deterministic natural-language classification;
- create a second prompt registry.
