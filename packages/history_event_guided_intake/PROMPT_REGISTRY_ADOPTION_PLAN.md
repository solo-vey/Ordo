# M65.1 — APF / History Event Factory Prompt Registry Adoption Plan

Status: `planned-adoption / no source YAML rewrite`
Milestone: `M65.1`
Depends on: `M65.0 Prompt Registry Standard`
Target package: `packages/history_event_guided_intake/`

## 1. Purpose

This plan defines how the History Event Factory / guided intake package should adopt the M65.0 Prompt Registry standard in a concrete, reviewable way.

The plan converts the backlog idea of small node-level prompts into a package migration path:

```text
prompt files → prompt_registry entries → node/artifact/repair prompt_refs → manifest coverage → validation gates → smoke test
```

This milestone does **not** rewrite `source/program.ordo.yaml` and does **not** create the final prompt files. It creates the adoption contract for the next package patch.

## 2. Scope

In scope:

- target `prompts/` folder structure;
- target `prompt_registry` YAML fragment;
- target node prompt reference placement;
- artifact helper prompt placement;
- repair helper prompt placement;
- README / START_HERE discoverability requirements;
- manifest coverage requirements;
- validation profile and smoke test plan;
- current-node to proposed-node mapping.

Out of scope:

- no runtime core behavior change;
- no parent CLI change;
- no opcode or IR promotion;
- no APF branch logic rewrite;
- no deterministic natural-language classifier;
- no actual source YAML migration until the plan is reviewed.

## 3. Target folder structure

```text
prompts/
  QUICK_START_PROMPT.md
  runtime/
    START_PROMPT_HISTORY_EVENT_FACTORY_RUNTIME_MODE.md
  nodes/
    hp.source_type.clarification.v1.md
    hp.source_row.intake.v1.md
    hp.normalization.value_comparison.v1.md
    hp.localization.bilingual_texts.v1.md
  artifacts/
    hp.artifact.history_event_passport.v1.md
    hp.artifact.jira_task.v1.md
    hp.artifact.implementation_prompt.v1.md
    hp.qa.package_generation.v1.md
  repair/
    hp.repair.gate_failure_explanation.v1.md
    hp.repair.backtracking_invalidation.v1.md
    hp.repair.missing_artifact_resolution.v1.md
```

## 4. Current package node mapping

The improvement proposal names several future/expanded APF nodes. The current imported `history_event.guided_intake` package uses a smaller MVP node set. M65.1 maps the proposal to the current package instead of pretending the future nodes already exist.

| Proposal node | Current package target | Adoption decision |
|---|---|---|
| `ROOT_N1` source type selection | `N_PATH_SELECT` | Use `hp.source_type.clarification.v1` as the first concrete helper. |
| `B4_N1` external ready fact intake | `N_SOURCE_FIELD` plus path C behavior | Plan as conditional helper for external fact path; do not add branch logic yet. |
| `B5_N3` comparison rule confirmation | `N_VALUE_SEMANTICS` and future comparison node | Plan helper now; split later if B5 nodes are promoted. |
| `COMMON_N4A` normalization | `N_VALUE_SEMANTICS` | Use one helper that explains comparison and output normalization boundaries. |
| `B1_N4B` human/UI texts | `N_DISPLAY_NAME_UK` / `N_DISPLAY_NAME_EN` | Use one display text helper; later split if title/description placeholders become separate nodes. |

## 5. Target prompt registry fragment

This fragment is the proposed source patch for a future M65.2-style implementation milestone. M65.1 records it as a plan only.

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
      path: prompts/hp.package.quick_start.v1.md
      required: true
      lifecycle: stable
      visibility: visible_to_analyst
      state_change_allowed: false
      validation_policy:
        - required_file_and_readme_reference
        - manifest_checksum_required

    - prompt_id: hp.runtime.start.v1
      type: runtime_start
      audience: human_to_ai
      path: prompts/hp.runtime.start.v1.md
      required: recommended
      lifecycle: stable
      visibility: visible_to_analyst
      state_change_allowed: false
      validation_policy:
        - required_file_only
        - authority_safe_text_review

    - prompt_id: hp.source_type.clarification.v1
      type: node_helper
      audience: ai_runtime
      path: prompts/hp.source_type.clarification.v1.md
      attached_to:
        node_id: N_PATH_SELECT
      required: recommended
      lifecycle: stable
      visibility: expose_on_request
      state_change_allowed: false
      validation_policy:
        - resolve_node_and_file
        - authority_safe_text_review
```

## 6. Target prompt refs

Target `prompt_refs` should be added only after prompt files and registry entries exist.

```yaml
nodes:
  - id: N_PATH_SELECT
    prompt_refs:
      - prompt_id: hp.source_type.clarification.v1
        use: during_clarification

  - id: N_SOURCE_FIELD
    prompt_refs:
      - prompt_id: hp.source_row.intake.v1
        use: during_clarification

  - id: N_VALUE_SEMANTICS
    prompt_refs:
      - prompt_id: hp.normalization.value_comparison.v1
        use: before_question
      - prompt_id: hp.normalization.value_comparison.v1
        use: during_clarification

  - id: N_DISPLAY_NAME_UK
    prompt_refs:
      - prompt_id: hp.localization.bilingual_texts.v1
        use: before_question

  - id: N_DISPLAY_NAME_EN
    prompt_refs:
      - prompt_id: hp.localization.bilingual_texts.v1
        use: before_question
```

## 7. Prompt authority rule

The package must preserve the M65.0 authority boundary:

```text
prompt files support execution; nodes/gates/state/CLI evidence own execution
```

Every helper prompt must state or imply:

- it cannot route to a different node;
- it cannot bypass a gate;
- it cannot silently mutate state;
- it cannot claim validation passed;
- it cannot invent artifacts, URLs, Jira keys, Confluence links, or confirmed requirements.

## 8. README and START_HERE requirements

`README.md` and `START_HERE_RUNTIME_MODE.md` should add a short note:

```text
For a tiny copy-paste startup prompt, use prompts/hp.package.quick_start.v1.md.
For full Runtime Mode rules, use START_HERE_RUNTIME_MODE.md and the embedded CLI protocol.
Node helper prompts are supportive guidance only; they do not replace gates, state, or CLI evidence.
```

`START_PROMPT_RUNTIME_MODE.md` may remain the full start prompt or be mirrored into `prompts/runtime/` after review.

## 9. Manifest requirements

A package manifest or packaging manifest should include every prompt file:

```json
{
  "prompts": [
    {
      "prompt_id": "hp.package.quick_start.v1",
      "path": "prompts/hp.package.quick_start.v1.md",
      "type": "package_bootstrap",
      "required": true,
      "sha256": "<computed during packaging>"
    }
  ]
}
```

If the current package does not yet have a prompt-aware manifest, M65.2 should add a package-local `PROMPT_MANIFEST.json` as a transitional file until parent packaging supports prompt entries.

## 10. Validation gates

The concrete adoption patch must pass these checks:

```text
prompt_registry_present = passed
prompt_ids_unique = passed
required_prompt_paths_exist = passed
node_prompt_refs_resolve = passed
node_prompt_refs_target_existing_nodes = passed
artifact_prompt_refs_resolve_or_marked_planned = passed
quick_start_discoverable = passed
prompt_manifest_coverage = passed
prompt_authority_safe = passed
state_change_policy_consistent = passed
runtime_start_protocol_not_weakened = passed
```

## 11. Smoke test plan

A minimal package smoke test should verify:

1. user can find `prompts/hp.package.quick_start.v1.md` from README;
2. quick prompt points to Runtime Mode entry and does not bypass CLI protocol;
3. at least one node helper is referenced from an existing node;
4. all prompt refs resolve to registry entries;
5. manifest contains prompt entries and checksums;
6. no helper prompt contains phrases like "ignore gate", "mark approved", "validation passed" without evidence.

## 12. Recommended rollout

| Step | Action | Status after M65.1 |
|---|---|---|
| 1 | Approve adoption plan | ready for review |
| 2 | Create prompt files as draft | future work |
| 3 | Add `prompt_registry` to source YAML | future work |
| 4 | Add `prompt_refs` to selected nodes | future work |
| 5 | Add manifest prompt entries | future work |
| 6 | Update README/START_HERE | future work |
| 7 | Run prompt registry validation/smoke test | future work |
| 8 | Promote prompts from draft to stable | future work after analyst review |

## 13. Readiness decision

M65.1 readiness: `ready-for-review`.

This is a safe adoption plan. It intentionally does not modify process execution until the prompt text and exact YAML patch are reviewed.

## M65.2 implementation status

The planned adoption has been implemented as a skeleton patch:

- prompt files are present under `prompts/`;
- `prompt_registry` is present in `source/program.ordo.yaml`;
- selected current nodes have `prompt_refs`;
- artifact helper refs are attached to package artifact definitions;
- gate failure and missing artifact repair helpers are referenced;
- `PROMPT_MANIFEST.json` lists prompt files with SHA-256 checksums.

This remains a package-local prompt-registry skeleton. Runtime/core/CLI enforcement is not promoted by this patch.
