# 19. Prompt Registry Model

Status: `M65.0 accepted source/schema convention`

## 1. Purpose

The Prompt Registry Model defines how Ordo/APF-style process packages may declare helper prompt files and connect them to nodes, artifacts, templates, gates, repair paths, and package startup flows.

The goal is to make small prompt files a first-class **package contract element** without turning them into runtime opcodes or process-structure owners.

## 2. Model position

The Prompt Registry sits beside the M64 first-wave program-level stack:

```text
program_contract
interaction_model
process_rail
conversation_semantics
program_level_approval_gate
prompt_registry
```

It is a package authoring and validation convention. Runtime behavior remains governed by process structure, state, gates, transitions, and human/CLI approval rules.

## 3. Core objects

### 3.1 `prompt_registry`

Top-level registry of reusable prompt entries that belong to the package.

Required identity fields:

```yaml
prompt_registry:
  registry_id: <stable id>
  version: "<version>"
  default_language: <language>
  prompt_root: prompts/
  prompts: []
```

### 3.2 Prompt entry

A prompt entry identifies a prompt file or prompt block:

```yaml
- prompt_id: hp.normalization.value_comparison.v1
  type: node_helper
  audience: ai_runtime
  path: prompts/hp.normalization.value_comparison.v1.md
  attached_to:
    node_id: B5_N3
  required: recommended
  lifecycle: stable
  visibility: expose_on_request
  state_change_allowed: false
```

### 3.3 `prompt_refs`

A node, artifact, template, or gate may use prompt refs:

```yaml
prompt_refs:
  - prompt_id: hp.normalization.value_comparison.v1
    use: before_question
```

Every `prompt_ref.prompt_id` must resolve to an entry in `prompt_registry.prompts` unless the package explicitly declares inherited registry behavior.

## 4. Authority boundary

Helper prompts may guide explanation, clarification, and formatting. They must not override:

- gates;
- transitions;
- state requirements;
- node completion conditions;
- program-level contracts;
- validation reports;
- human final approval.

This rule is strict even if a prompt file contains stronger language. Structural process contracts have priority over helper prompt text.

## 5. State-change policy

Prompts should declare whether they may directly lead to state updates:

```yaml
state_change_allowed: false
```

A prompt marked `state_change_allowed: false` may help the AI ask or clarify, but the state update still requires the normal node answer, gate, and checkpoint path.

## 6. Visibility policy

Prompt visibility controls what may be shown to a human by default:

| Visibility | Default behavior |
|---|---|
| `visible_to_analyst` | Safe to show directly. |
| `model_internal` | Do not show by default. May be summarized if needed. |
| `expose_on_request` | Can be shown or summarized when asked. |

Visibility is about presentation, not secrecy. It does not authorize hidden state changes.

## 7. Manifest integration

Prompt files should be listed in package manifest:

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

For M65.0 this is a packaging convention and future validation target.

## 8. Trace awareness

A runtime trace, session trace, or human review report may record prompt refs used:

```json
{
  "node_id": "B5_N3",
  "prompt_refs_used": ["hp.normalization.value_comparison.v1"]
}
```

The trace should record prompt usage as audit metadata, not as a substitute for evidence of gate success.

## 9. Validation model

Future validators should check:

- registry exists when prompt files are contractual;
- prompt ids are unique;
- prompt paths exist;
- required prompts are present;
- prompt refs resolve;
- attached node/artifact/template ids exist;
- visibility is declared or inherited;
- language is declared or inherited;
- helper prompts do not override structural authority;
- prompt files are included in manifest;
- quick-start prompt is discoverable from README/START_HERE.

## 10. Warning model

Future validators may warn when:

- a complex node has no helper prompt;
- prompt file exists but is not referenced;
- prompt content is duplicated across many nodes;
- a stable prompt references deprecated node/artifact ids;
- a human-facing quick-start prompt exists but is not listed in README/START_HERE.

## 11. Non-goals

M65.0 does not introduce:

- `PROMPT.REGISTRY` opcode;
- runtime-core behavior;
- compiler enforcement;
- CLI command implementation;
- deterministic natural-language prompt validation;
- APF package rewrite.

## 12. Acceptance criteria for package adoption

A package adopts the Prompt Registry convention when:

1. `prompt_registry` exists;
2. prompt files are listed with stable ids;
3. node/artifact prompt refs resolve;
4. required prompt paths exist;
5. quick-start prompt is discoverable;
6. manifest coverage exists or is explicitly deferred;
7. helper prompts are marked supportive and do not override gates/state.
