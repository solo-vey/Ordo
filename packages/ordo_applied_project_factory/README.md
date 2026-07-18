# ordo.applied_project_factory

`ordo.applied_project_factory` creates or improves applied Ordo projects through PM/analyst dialogue while hiding YAML by default.

Module version: `0.1.0-rc.1`  
Compatible language package: `Ordo 0.12.0-preview-rc1`  
Release channel: `release-candidate`  
Parent language line: `M62 line closure`  
Versioning scope: `module_local`

## Release-candidate scope

```text
- four startup modes are closed: domain model + tree, manual tree, free dialogue, existing process improvement
- shared output/template subflow is closed
- shared validation/handoff tail is closed
- whole-tree integration review is closed
- real validation has no blocking issues under the M62 parent CLI profile
- FLOW.JOIN / SHARED.TAIL.REFERENCE remain future language candidates, not RC runtime-core changes
```

## Authoring modes

```text
1. Доменна модель + дерево рішень
2. Ручне дерево рішень
3. Вільний діалог
4. Коригування існуючого процесу
```

## Developer validation pipeline for this RC

From the parent M62 workspace root:

```bash
PYTHONPATH=cli:. python -m cli.ordo.cli lint packages/ordo_applied_project_factory
PYTHONPATH=cli:. python -m cli.ordo.cli compile packages/ordo_applied_project_factory
PYTHONPATH=cli:. python -m cli.ordo.cli test packages/ordo_applied_project_factory
PYTHONPATH=cli:. python -m cli.ordo.cli coverage packages/ordo_applied_project_factory
PYTHONPATH=cli:. python -m cli.ordo.cli validate-state packages/ordo_applied_project_factory --state packages/ordo_applied_project_factory/run_inputs/rc1_full_validation_state.yaml
PYTHONPATH=cli:. python -m cli.ordo.cli next-step packages/ordo_applied_project_factory --state packages/ordo_applied_project_factory/run_inputs/rc1_full_validation_state.yaml
PYTHONPATH=cli:. python -m cli.ordo.cli validate-output packages/ordo_applied_project_factory
PYTHONPATH=cli:. python -m cli.ordo.cli validate-artifacts packages/ordo_applied_project_factory --state packages/ordo_applied_project_factory/run_inputs/rc1_full_validation_state.yaml
PYTHONPATH=cli:. python -m cli.ordo.cli consistency packages/ordo_applied_project_factory --state packages/ordo_applied_project_factory/run_inputs/rc1_full_validation_state.yaml
PYTHONPATH=cli:. python -m cli.ordo.cli go-no-go packages/ordo_applied_project_factory --state packages/ordo_applied_project_factory/run_inputs/rc1_full_validation_state.yaml
```

Status: `release-candidate / go with non-blocking warnings`.


---

# ordo.applied_project_factory

`ordo.applied_project_factory` creates new applied Ordo projects through PM/analyst dialogue while hiding YAML by default.

Module version: `0.1.0-alpha.15`  
Compatible language package: `Ordo 0.12.0-preview-rc1`  
Versioning scope: `module_local`

## Current scope

```text
- any Ordo process type, not only document-generating projects
- PM/analyst does not write YAML directly
- first generated output is source/program.ordo.yaml
- output template contracts are collected immediately
- confusion/self-test generation is deferred until after tree approval
- focused/context SVG is the default working graph view
- language improvement proposals are captured as an artifact
- process feedback can update/reload the YAML after user approval
- free-dialogue extraction is shown as plain-language sections, not a technical alias dump
- every current-node review includes a human-readable description
- SVG is generated only when explicitly requested by the user
- current-node review shows state, gates, artifacts/templates, and open/deferred sibling branches
- depth-first review tracks confirmed path, current branch, unreviewed siblings, and deferred return points
- incremental YAML patches are used after confirmed tree steps when YAML changes are needed
- per-step checks stay minimal; full CLI validation is a terminal/pre-handoff gate
- runtime review separates unreviewed sibling branches from not-selected control actions and blocked-until-ready actions
```

## Authoring modes

```text
1. Доменна модель + дерево рішень
2. Ручне дерево рішень
3. Вільний діалог
```

Mode 3 is now stabilized as a self-hosted loop:

```text
raw notes → structured extraction → “що далі?” trigger → draft tree → depth-first review/correction → stabilized branch handoff
```

## Versioning decision

This package is not numbered as a whole-language milestone. It has its own module version. The parent Ordo language package may later include this module at an explicit version.

See:

```text
VERSION.md
MODULE_CHANGELOG.md
docs/MODULE_VERSIONING_POLICY.md
```

## Graph policy

Default working graph:

```text
context view = root path → current node → current subtree
```

Full tree is only an overview. `ordo_visual_graph_generator 1.1.0-preview` annotations may be used as an optional review layer.

See:

```text
docs/FOCUSED_GRAPH_RENDERING_POLICY.md
docs/GRAPH_ANNOTATION_OVERLAY_POLICY.md
```

## Developer validation pipeline

```bash
python -m cli.ordo.cli lint packages/ordo_applied_project_factory
python -m cli.ordo.cli compile packages/ordo_applied_project_factory
python -m cli.ordo.cli test packages/ordo_applied_project_factory
python -m cli.ordo.cli coverage packages/ordo_applied_project_factory
python -m cli.ordo.cli validate-state packages/ordo_applied_project_factory --answers packages/ordo_applied_project_factory/run_inputs/factory_success.yaml
python -m cli.ordo.cli next-step packages/ordo_applied_project_factory --answers packages/ordo_applied_project_factory/run_inputs/factory_success.yaml
python -m cli.ordo.cli validate-factory-output packages/ordo_applied_project_factory/generated_examples/decision_note_assistant
```

Status: prototype / ready-for-review.

## Runtime entry files

Use these files when running the package in runtime mode:

```text
START_HERE_RUNTIME_MODE.md
START_PROMPT_RUNTIME_MODE.md
compiled/program.ir.json
```

`compiled/program.ir.json` is generated by the compile step and must not be edited manually.

## Runtime review discipline v0.1.0-alpha.11

The user-facing current node review requires `current_node_review_includes_state_gates_artifacts` and `sibling_branches_tracked_during_depth_first_review`.

Runtime state tracks `node_review_display_contract`, `confirmed_review_path`, `current_review_branch`, `unreviewed_sibling_branches`, `deferred_return_points`, and `current_node_review_record`.


## Incremental validation discipline v0.1.0-alpha.11

During tree review, confirmed decisions should be persisted without forcing a full package validation cycle after every node.

Runtime rule:

```text
confirmed tree step
→ if YAML needs changing: apply a small scoped YAML patch
→ run minimal check: yaml_parse + lint + compile refresh
→ continue review from updated YAML
```

Full validation is reserved for terminal/pre-handoff points:

```text
lint → compile → test → coverage → validate-state → next-step → validate-factory-output → repo-check
```

If full validation finds inconsistency or missing information, the runtime returns to tree/YAML correction instead of marking the project ready.


## Runtime decision gate discipline v0.1.0-alpha.11

When a current node exposes explicit options, APF must ask the user to choose one of those options. The node-review approval/correction/deferment step is a control gate, not a content node that gets generic confirmation.

## Runtime control-action bookkeeping v0.1.0-alpha.13

During runtime review, the model must not mix three different concepts:

```text
unreviewed_sibling_branches = real tree branches that still need traversal
not_selected_control_actions = available runtime actions intentionally not chosen now
blocked_until_ready_actions = actions visible but not allowed until readiness conditions pass
```

Example: after choosing `approve_current_node`, `correct_current_node` and `defer_current_node` are recorded as not selected, not as return points. If `continue_depth_first` is chosen while branches remain, `approve_tree` is recorded as blocked until all required branches are reviewed.


## Runtime rendering contract v0.1.0-alpha.13

During process-design review, APF must explicitly show the current interaction mode before asking the user to choose. The rendered current-node block must distinguish tree traversal / branch selection from node-review decisions and execution gates, and must show state, gates, artifacts, pending sibling/deferred branches, plus the appropriate decision prompt.

## Branch 1 progressive authoring v0.1.0-alpha.15

Alpha.15 closes the human review of the **Доменна модель + дерево рішень** branch. The branch now uses progressive tree authoring instead of a one-shot static blueprint, treats input artifacts as policy-based rather than mandatory, separates output artifact candidates from output templates, and requires terminal output binding plus template/mock-filled-example review before a terminal path is considered ready.

The shared full-validation / handoff tail remains shared and is not duplicated in branch 1.

<!-- APF alpha.21 full-validation contract coverage appendix -->

## APF alpha.21 full-validation contract coverage appendix

This appendix records confirmed contract fields for deterministic artifact coverage validation. It is a technical release-readiness section and does not change the user-facing APF process logic.

- `any_ordo_process_type_allowed`: `true`
- `pm_does_not_write_yaml`: `true`
- `first_output_source_yaml_only`: `true`
- `confusion_tests_deferred`: `true`
- `templates_generated_immediately`: `true`
- `separate_package_from_project_builder`: `true`
- `three_authoring_modes_supported`: `true`
- `free_dialogue_draft_review_loop`: `true`
- `test_cases_after_tree_approval`: `true`
- `self_hosted_authoring_loop`: `true`
- `free_dialogue_structured_extraction`: `true`
- `stabilized_branch_reuse`: `true`
- `focused_svg_context_by_default`: `true`
- `language_improvement_proposals_artifact`: `docs/LANGUAGE_IMPROVEMENT_PROPOSALS.md`
- `svg_generated_only_on_request`: `true`
- `current_node_description_required`: `true`
- `plain_language_extraction_summary_required`: `true`
- `process_feedback_can_update_yaml_after_approval`: `true`
- `current_node_review_includes_state_gates_artifacts`: `true`
- `sibling_branches_tracked_during_depth_first_review`: `true`


## 0.1.0-alpha.21 validation note

Full-validation readiness patch: version alignment, static coverage backfill, contract coverage appendices, and full-validation state fixture. Process logic unchanged.


## M63.3 RC language-pattern classification

APF `v0.1.0-rc.1` is used as a standard applied-module pattern source. Pattern candidates are classified in `docs/APF_RC_LANGUAGE_PATTERN_CLASSIFICATION.md`; they are not automatically promoted into parent IR/runtime semantics.
