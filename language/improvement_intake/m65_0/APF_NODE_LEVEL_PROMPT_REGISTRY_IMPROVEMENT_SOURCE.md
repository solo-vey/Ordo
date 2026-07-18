# Improvement Proposal: Node-Level Prompt Registry and Prompt References

**Scope:** Ordo / APF model standard + History Event Analysis Package Factory process  
**Status:** proposed improvement  
**Created for:** AI ARTEMIDA TECHNOLOGIES / History Event Analysis Package Factory v0.8 follow-up  
**Purpose:** make small node-specific assistant prompts a first-class, versioned, validated part of process packages instead of ad-hoc free text hidden inside nodes.

---

## 1. Problem

Current applied process packages can describe nodes, gates, transitions, state fields, artifacts, templates, and runtime behavior. However, small helper prompts that guide the AI inside a specific node are not yet treated as a first-class package element.

Today, these instructions are usually embedded directly inside a node as freeform fields such as:

- `question`
- `purpose`
- `ai_must_present`
- `notes`
- `must_not`
- gate checks

This works for small processes, but it becomes fragile when the process grows.

The issue is not only technical. It affects how an analyst experiences the package:

- the process knows the node structure, but not always the best conversational behavior for that node;
- mini-prompts are mixed with structural process logic;
- node guidance is harder to reuse, review, translate, version, or validate;
- quick prompts such as `QUICK_START_PROMPT.md` do not have a standard place in the model;
- package creators may invent inconsistent folder names and prompt attachment conventions;
- runtime cannot easily validate whether a node references an existing helper prompt;
- generated packages may contain helpful prompt files, but they are not clearly part of the process contract.

The desired improvement is to make node-level and package-level helper prompts explicit, discoverable, validated, and connected to the process model.

---

## 2. Target Concept

Introduce a standard **Prompt Registry** for applied process packages.

A process package should be able to declare:

1. package-level prompts, such as a short bootstrap prompt;
2. runtime/start prompts;
3. node-level helper prompts;
4. artifact-generation prompts;
5. repair/recovery prompts;
6. human-facing explanation prompts;
7. model-facing execution prompts.

These prompts should not replace nodes or gates. They should support them.

The node remains the source of process structure:

- what step this is;
- what must be confirmed;
- what state changes;
- which gate applies;
- where the process goes next.

The helper prompt describes how the AI should conduct that step:

- how to explain the step to a human;
- which examples to show;
- which clarifying questions are allowed;
- which technical details should be hidden unless requested;
- how to avoid over-confirming or silently changing state;
- how to summarize the result of the step.

---

# Part A — Improvement for the Ordo / APF Model Standard

This part should be considered a model/language/process-standard improvement.

## A.1. Add `PROMPT.REGISTRY` / `prompt_registry`

### Purpose

Define all reusable prompt files or inline prompt blocks that are part of a process package.

### Suggested top-level structure

```yaml
prompt_registry:
  registry_id: history_event_factory_prompt_registry
  version: "0.1"
  default_language: uk
  prompt_root: prompts/
  prompts:
    - prompt_id: quick_start_prompt
      type: package_bootstrap
      audience: human_to_ai
      path: prompts/QUICK_START_PROMPT.md
      required: true
      lifecycle: stable

    - prompt_id: root_source_type_clarification
      type: node_helper
      audience: ai_runtime
      path: prompts/nodes/ROOT_N1_source_type_clarification.md
      attached_to:
        node_id: ROOT_N1
      required: recommended
      lifecycle: stable
```

### Recommended fields

| Field | Meaning |
|---|---|
| `prompt_id` | stable prompt identifier |
| `type` | package_bootstrap, runtime_start, node_helper, artifact_helper, repair_helper, validation_helper |
| `audience` | human_to_ai, ai_runtime, developer, analyst, cli_operator |
| `path` | package-relative file path |
| `attached_to.node_id` | node this prompt supports, if node-specific |
| `attached_to.artifact_id` | artifact/template this prompt supports, if artifact-specific |
| `required` | true / false / recommended / conditional |
| `language` | prompt language, if different from default |
| `lifecycle` | draft, stable, deprecated |
| `visibility` | visible_to_analyst, model_internal, expose_on_request |
| `state_change_allowed` | whether the prompt may lead to state update directly |
| `validation_policy` | how runtime should validate presence and consistency |

---

## A.2. Add node-level `prompt_refs`

Nodes should be able to reference prompts without embedding all guidance inline.

Example:

```yaml
nodes:
  - id: B5_N3
    type: confirmation
    question: Confirm comparison rule for previous/current external data block.
    prompt_refs:
      - prompt_id: B5_N3_comparison_rule_helper
        use: before_question
      - prompt_id: B5_N3_comparison_rule_summary
        use: after_answer
```

### Suggested `use` values

| Use | Meaning |
|---|---|
| `before_question` | helps AI introduce the node |
| `during_clarification` | helps AI answer clarification without changing state |
| `after_answer` | helps AI summarize and confirm result |
| `on_gate_fail` | helps AI explain blocker and repair path |
| `on_backtrack` | helps AI explain invalidation/review consequences |
| `artifact_generation` | helps generate an artifact from confirmed state |

---

## A.3. Add prompt validation rules

The compiler/runtime should validate prompt references.

### Required checks

- every `prompt_ref` points to a prompt in `prompt_registry`;
- every prompt path exists in the package;
- required prompts are present;
- node helper prompts only reference existing nodes;
- prompt visibility is declared;
- prompt language is declared or inherits package default;
- prompt does not claim authority over gates/transitions unless the node allows it;
- prompts marked `state_change_allowed: false` must not be used as state-changing instructions.

### Warning checks

- node has complex behavior but no helper prompt;
- prompt file exists but is not referenced anywhere;
- duplicated prompt content across many nodes;
- prompt is marked stable but references deprecated node/artifact ids;
- human-facing quick start prompt exists but is not listed in README / START_HERE.

---

## A.4. Add prompt roles to interaction model

The interaction model should distinguish:

1. structural node logic;
2. helper prompt behavior;
3. human confirmation;
4. CLI validation.

Recommended rule:

> Helper prompts may guide explanation, clarification, and formatting, but must not override gates, transitions, state requirements, or confirmed process contracts.

---

## A.5. Add prompt packaging standard

Recommended package structure:

```text
prompts/
  QUICK_START_PROMPT.md
  runtime/
    START_PROMPT_HISTORY_EVENT_FACTORY_RUNTIME_MODE.md
  nodes/
    ROOT_N1_source_type_clarification.md
    B4_N1_external_fact_intake_helper.md
    B5_N3_comparison_rule_helper.md
    COMMON_N4A_normalization_helper.md
    B1_N4B_human_ui_texts_helper.md
  artifacts/
    passport_generation_helper.md
    jira_task_generation_helper.md
    qa_package_generation_helper.md
  repair/
    gate_failure_explanation_helper.md
```

---

## A.6. Add manifest integration

`MANIFEST.json` should list prompt files and classify them.

Example:

```json
{
  "prompts": [
    {
      "prompt_id": "quick_start_prompt",
      "path": "prompts/QUICK_START_PROMPT.md",
      "type": "package_bootstrap",
      "required": true,
      "sha256": "..."
    }
  ]
}
```

---

## A.7. Add runtime trace awareness

When a node helper prompt is used, runtime trace may record:

```json
{
  "node_id": "B5_N3",
  "prompt_refs_used": ["B5_N3_comparison_rule_helper"]
}
```

This improves auditability without exposing all model internals to the analyst.

---

## A.8. Add prompt-specific gates or checks

Introduce a package-level gate such as:

```yaml
PROMPT_REGISTRY_CONSISTENCY_GATE:
  type: hard_with_warning_support
  checks:
    - all required prompt files exist
    - all node prompt_refs resolve
    - QUICK_START_PROMPT exists and is referenced from README / START_HERE
    - helper prompts do not override node/gate authority
    - prompt files are included in MANIFEST
```

---

# Part B — Improvement for History Event Analysis Package Factory

This part should be applied to the concrete process that generates History Event analytical packages/playbooks.

## B.1. Add prompt registry to the factory package

The History Event Analysis Package Factory should include:

```text
prompts/
  QUICK_START_PROMPT.md
  nodes/
  artifacts/
  repair/
```

The first required prompt should be:

```text
prompts/QUICK_START_PROMPT.md
```

Purpose: give the analyst a tiny copy-paste prompt for starting a new chat with the package.

Suggested content:

```text
Запусти History Event Analysis Package Factory v0.8 з наданого файлу.
Веди мене по процесу по одному кроку, людською мовою, без YAML якщо я не попрошу.
Почни з першого питання: Яка історична подія потрібна?
```

---

## B.2. Add node helper prompts for high-value nodes

Start with these nodes:

### ROOT_N1 — source type selection

Prompt file:

```text
prompts/nodes/ROOT_N1_source_type_clarification.md
```

Purpose:

- explain five supported source paths in plain language;
- clarify unclear input without using fallback option 6;
- map uncertain user answers to paths 1–5 only;
- avoid technical YAML output.

### B4_N1 — external ready fact intake

Prompt file:

```text
prompts/nodes/B4_N1_external_fact_intake_helper.md
```

Purpose:

- help analyst provide an external event/fact example;
- avoid asking for ChangeRecord or Mongo row;
- distinguish ready fact from data block comparison.

### B5_N3 — comparison rule confirmation

Prompt file:

```text
prompts/nodes/B5_N3_comparison_rule_helper.md
```

Purpose:

- explain previous/current comparison in simple terms;
- ask about matching key, compared fields, ignored fields, normalization;
- prevent creating events from volatile technical fields.

### COMMON_N4A — normalization

Prompt file:

```text
prompts/nodes/COMMON_N4A_normalization_helper.md
```

Purpose:

- explain raw value → normalized value;
- cover null/missing/empty behavior;
- distinguish comparison normalization from final HistoryEvent value normalization.

### B1_N4B — human/UI texts

Prompt file:

```text
prompts/nodes/B1_N4B_human_ui_texts_helper.md
```

Purpose:

- keep this step human-readable;
- ask for title, short description, long description, placeholders, fallback behavior, QA text assertions;
- prevent AI from inventing display text outside confirmed state.

---

## B.3. Add artifact helper prompts

Recommended files:

```text
prompts/artifacts/passport_generation_helper.md
prompts/artifacts/jira_task_generation_helper.md
prompts/artifacts/implementation_prompt_generation_helper.md
prompts/artifacts/qa_package_generation_helper.md
```

Purpose:

- keep generated artifacts aligned with confirmed state;
- ensure path 5 includes “Comparison-to-HistoryEvent algorithm”;
- ensure no invented Confluence/Jira URLs;
- ensure implementation prompt clearly separates confirmed requirements from open questions.

---

## B.4. Add repair helper prompts

Recommended files:

```text
prompts/repair/gate_failure_explanation_helper.md
prompts/repair/backtracking_invalidation_helper.md
prompts/repair/missing_artifact_resolution_helper.md
```

Purpose:

- explain blockers in human language;
- tell analyst what is missing;
- avoid raw YAML/tool output unless requested;
- resume the interrupted node after repair.

---

## B.5. Update process YAML

Add top-level prompt registry:

```yaml
prompt_registry:
  registry_id: history_event_factory_prompt_registry
  version: "0.1"
  default_language: uk
  prompt_root: prompts/
  prompts:
    - prompt_id: quick_start_prompt
      type: package_bootstrap
      audience: human_to_ai
      path: prompts/QUICK_START_PROMPT.md
      required: true
      visibility: visible_to_analyst
```

Add node prompt refs, for example:

```yaml
nodes:
  - id: ROOT_N1
    prompt_refs:
      - prompt_id: ROOT_N1_source_type_clarification
        use: during_clarification
```

---

## B.6. Update README / START_HERE

README and START_HERE should explicitly say:

1. for a tiny copy-paste start, use `prompts/QUICK_START_PROMPT.md`;
2. for full runtime behavior, use `START_PROMPT_HISTORY_EVENT_FACTORY_RUNTIME_MODE.md`;
3. node helper prompts are internal process aids, not replacements for gates;
4. YAML is not required for normal analyst usage.

---

## B.7. Update package validation

Add checks:

- prompt registry exists;
- quick start prompt exists;
- referenced node prompts exist;
- prompt files are listed in manifest;
- prompt files included in zip;
- no stale prompt refs;
- no prompt claims to override gates or confirmed state.

---

## B.8. Update graph/full documentation

Graph output does not need to show all prompt files by default, but full mode may show a small annotation:

```text
B5_N3
  helper prompt: B5_N3_comparison_rule_helper
```

Tree-only mode should remain clean and show only nodes and branches.

---

# Part C — Consistency Rules Between Model and Process

To avoid ad-hoc implementation, the same standard should exist at both levels.

## C.1. Model-level standard

The Ordo/APF model should support:

- `prompt_registry`;
- `prompt_refs` on nodes/artifacts/gates;
- manifest integration;
- prompt consistency validation;
- prompt visibility rules;
- trace awareness.

## C.2. Process-level implementation

The History Event Analysis Package Factory should use that standard by including:

- `prompts/QUICK_START_PROMPT.md`;
- selected node helper prompts;
- artifact helper prompts;
- repair helper prompts;
- prompt registry in YAML;
- README/START_HERE references;
- validation and manifest coverage.

## C.3. Important rule

Prompt files are not a replacement for the process model.

They are supportive guidance only.

A helper prompt must not:

- change routing by itself;
- bypass a gate;
- silently confirm state;
- override program-level contract;
- invent output artifacts;
- claim CLI validation succeeded.

---

# Part D — Acceptance Criteria

This improvement is complete when:

1. the model standard defines prompt registry and prompt references;
2. package compiler/validator can detect missing prompt refs;
3. History Event Factory package includes `prompts/QUICK_START_PROMPT.md`;
4. at least five high-value nodes have helper prompt files;
5. README and START_HERE tell the analyst which prompt to use;
6. MANIFEST lists prompt files;
7. final package composition gate checks prompt files;
8. runtime/startup smoke test verifies quick-start discoverability;
9. helper prompts are clearly marked as supportive and cannot override gates/state.

---

# Part E — Suggested Versioning

Recommended target versions:

- Ordo/APF model standard: next minor version, because this adds a new package structure capability.
- History Event Analysis Package Factory: v0.8.1 or v0.9, depending on whether this is treated as a small enhancement or a package structure upgrade.

Recommended rollout:

1. add `QUICK_START_PROMPT.md` first;
2. add prompt registry skeleton;
3. attach helper prompts to selected nodes;
4. update validation and manifest;
5. regenerate README/START_HERE;
6. run smoke test;
7. package new version.

