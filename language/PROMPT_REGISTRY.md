# Prompt Registry Standard

Status: `M65.0 accepted schema convention / docs-lint-profile design`

M65.0 introduces the **Prompt Registry** as a package-level convention for declaring small helper prompts that are part of a process package contract.

The registry makes package, runtime, node, artifact, repair, and validation helper prompts explicit, discoverable, reviewable, versioned, and validateable. It is not a runtime opcode and does not give prompt files authority over process structure.

```text
process structure remains authoritative
  → nodes define steps, state, gates, transitions, outputs
helper prompts support execution
  → explanation, clarification, formatting, repair guidance, artifact drafting
validation checks the connection
  → prompt ids resolve, paths exist, authority is safe, manifest coverage is visible
```

## Why this layer exists

Applied process packages often contain small assistant instructions inside node fields such as `question`, `purpose`, `ai_must_present`, `notes`, `must_not`, and gate descriptions. This is usable for small packages, but fragile for large guided factories.

The Prompt Registry separates **structural process logic** from **conversation guidance**:

- nodes remain the source of state, gates, transitions, and routing;
- helper prompts explain how the AI should conduct a node or artifact step;
- registry entries make helper prompts reusable, reviewable, translated, deprecated, and checked;
- package readers can find quick-start prompts without guessing folder names;
- future linters can detect missing or stale prompt references.

## Canonical source shape

A package may declare top-level `prompt_registry` in `source/program.ordo.yaml`:

```yaml
prompt_registry:
  registry_id: history_event_factory_prompt_registry
  version: "0.1"
  default_language: uk
  prompt_root: prompts/
  prompts:
    - prompt_id: hp.package.quick_start.v1
      type: package_bootstrap
      audience: human_to_ai
      path: prompts/QUICK_START_PROMPT.md
      required: true
      lifecycle: stable
      visibility: visible_to_analyst
      state_change_allowed: false
      validation_policy: required_file_and_readme_reference

    - prompt_id: hp.source_type.clarification.v1
      type: node_helper
      audience: ai_runtime
      path: prompts/hp.source_type.clarification.v1.md
      attached_to:
        node_id: ROOT_N1
      required: recommended
      lifecycle: stable
      visibility: expose_on_request
      state_change_allowed: false
      validation_policy: resolve_node_and_file
```

This block is a source/schema convention in M65.0. It documents the shape for package authors and future validators.

## Node-level `prompt_refs`

Nodes may reference helper prompts without embedding all guidance inline:

```yaml
nodes:
  - id: B5_N3
    type: confirmation
    question: Confirm comparison rule for previous/current external data block.
    prompt_refs:
      - prompt_id: hp.normalization.value_comparison.v1
        use: before_question
      - prompt_id: hp.normalization.value_comparison_summary.v1
        use: after_answer
```

`prompt_refs` may also be used on artifacts, templates, gates, or package assembly steps if the package standard declares those attachment points.

## Prompt files are supportive only

Helper prompts may guide:

- plain-language explanation;
- clarification questions;
- formatting of assistant output;
- examples shown to an analyst;
- repair or backtracking explanation;
- artifact-generation guidance derived from confirmed state.

Helper prompts must not:

- change routing by themselves;
- bypass gates;
- silently confirm or mutate state;
- override `program_contract`, `interaction_model`, `process_rail`, or `conversation_semantics`;
- invent output artifacts;
- claim validation succeeded without evidence.

Recommended rule:

```text
Prompt files support execution. They do not own execution.
```

## Relationship to M64 first-wave contracts

| M64/M65 block | Relationship |
|---|---|
| `program_contract` | declares package identity, lifecycle, authority, validation expectations |
| `interaction_model` | declares human/AI/CLI roles and authority boundaries |
| `process_rail` | declares state, resume, deviation, and backtracking behavior |
| `conversation_semantics` | declares input classes and routing behavior |
| `program_level_approval_gate` | checks program-level contract completeness by profile |
| `prompt_registry` | declares supportive prompts and their safe attachment points |

M65.0 depends conceptually on the M64 stack because prompt guidance must respect program-level authority and process rail rules.

## Prompt categories

| Type | Purpose |
|---|---|
| `package_bootstrap` | tiny copy-paste prompt for starting a package in a new chat |
| `runtime_start` | full runtime-mode start prompt |
| `node_helper` | guidance for a specific node |
| `artifact_helper` | guidance for generating a specific artifact/template |
| `repair_helper` | explanation and recovery after blocker/gate failure |
| `validation_helper` | guidance for validation report interpretation |
| `human_explanation` | analyst-facing explanatory prompt |
| `model_execution` | model-facing execution discipline prompt |

## Recommended package structure

```text
prompts/
  QUICK_START_PROMPT.md
  runtime/
    START_PROMPT_<PACKAGE>_RUNTIME_MODE.md
  nodes/
    hp.source_type.clarification.v1.md
    hp.normalization.value_comparison.v1.md
  artifacts/
    passport_generation_helper.md
    jira_task_generation_helper.md
    qa_package_generation_helper.md
  repair/
    gate_failure_explanation_helper.md
    backtracking_invalidation_helper.md
```

The exact folder names may be package-local, but `prompt_root` and registry entries must make them discoverable.

## Manifest integration

`MANIFEST.json` should list prompt files and classify them:

```json
{
  "prompts": [
    {
      "prompt_id": "hp.package.quick_start.v1",
      "path": "prompts/QUICK_START_PROMPT.md",
      "type": "package_bootstrap",
      "required": true,
      "sha256": "..."
    }
  ]
}
```

Manifest integration is a packaging/checksum convention. It does not execute prompts.

## Trace awareness

A runtime or reviewer may record which prompt refs were used:

```json
{
  "node_id": "B5_N3",
  "prompt_refs_used": ["hp.normalization.value_comparison.v1"]
}
```

This improves auditability without requiring exposure of all model-internal reasoning.

## Prompt registry consistency gate

Future validation should expose a package-level gate:

```yaml
PROMPT_REGISTRY_CONSISTENCY_GATE:
  type: hard_with_warning_support
  checks:
    - all required prompt files exist
    - all prompt_refs resolve to prompt_registry entries
    - node helper prompts reference existing nodes
    - QUICK_START_PROMPT exists and is referenced from README or START_HERE
    - helper prompts do not claim authority over gates, transitions, or confirmed state
    - prompt files are listed in MANIFEST
```

M65.0 only defines this as a documentation/schema/lint-profile design gate. CLI enforcement is future work.

## Non-goals

M65.0 does not introduce:

- new opcodes;
- runtime-core execution behavior;
- deterministic natural-language prompt interpretation;
- compiler enforcement;
- parent CLI commands;
- APF source YAML rewrite.

## Typical mistakes

- Treating a helper prompt as a node or gate.
- Embedding state-changing instructions in a prompt marked `state_change_allowed: false`.
- Creating prompt files without registry entries.
- Referencing non-existing node ids from prompt attachments.
- Adding a quick-start prompt but not linking it from README or START_HERE.
- Letting artifact helper prompts invent fields outside confirmed state.
