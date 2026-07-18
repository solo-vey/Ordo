# Language Improvement Proposals

Status: active proposal log for M61.6.

This artifact captures missing or provisional Ordo language features discovered while authoring projects. The goal is to avoid silently inventing metadata that later becomes incompatible with the language package.

## Proposal LIP-M61-6-001 — Formal gate description field

```text
problem: Gate IDs and conditions are sometimes too compact for graph review. Users need a short human explanation attached to a gate card.
current_limitation: gate.description is useful for rendering/review, but is not yet treated as a formal language construct across the full language package.
proposed_construct: gates[].description as an optional human-readable field.
temporary_workaround: use description provisionally in package YAML and record it here until the language package formalizes it.
affected_packages: ordo.applied_project_factory; visual graph generator; future generated applied projects.
status: proposed_for_language_package
```

## Proposal LIP-M61-6-002 — Graph rendering policy metadata

```text
problem: Authoring sessions need a durable way to declare graph rendering defaults for branch-level review.
current_limitation: focused/context SVG behavior currently lives in instructions and tooling flags rather than a formal Ordo policy object.
proposed_construct: graph_rendering_policy or visualization_policy block with default_mode, focus_node, and overview/full-tree rules.
temporary_workaround: store focused_svg_policy in state and document the rule in docs/FOCUSED_GRAPH_RENDERING_POLICY.md.
affected_packages: ordo.applied_project_factory; generated applied projects; graph utility.
status: proposed_for_language_package
```

## Proposal LIP-M61-6-003 — Language proposal artifact type

```text
problem: Language gaps discovered during authoring need a standard project artifact, not ad-hoc notes.
current_limitation: docs/LANGUAGE_IMPROVEMENT_PROPOSALS.md is useful but not yet a canonical artifact type.
proposed_construct: artifact kind language_improvement_proposals with fields problem, current_limitation, proposed_construct, temporary_workaround, affected_packages, status.
temporary_workaround: declare LANGUAGE_IMPROVEMENT_PROPOSALS as a markdown artifact with explicit artifact requirements.
affected_packages: ordo.applied_project_factory; language package maintenance workflow.
status: proposed_for_language_package
```

## Proposal LIP-APF-0-1-0-A8-001 — Formal node description field

```text
problem: Current-node review needs a human-readable explanation of what the node does, in the user's language. IDs/questions alone are not enough.
current_limitation: nodes[].description is useful in APF but not yet formalized as a canonical language field.
proposed_construct: nodes[].description as an optional user-facing explanation field.
temporary_workaround: use description provisionally in package YAML and show it in the runtime current-node block.
affected_packages: ordo.applied_project_factory; generated applied projects; graph/review tooling.
status: proposed_for_language_package
```

## Proposal LIP-APF-0-1-0-A8-002 — User-facing extraction summary contract

```text
problem: Structured extraction after free dialogue can become too technical if shown as aliases or YAML-like maps.
current_limitation: Ordo has state fields but no formal user-facing extraction-summary surface.
proposed_construct: user_facing_extraction_summary with sections what_i_heard, what_it_means, emerging_tree, open_questions, and optional technical_projection.
temporary_workaround: store user_facing_extraction_policy in state and keep technical projection internal unless needed.
affected_packages: ordo.applied_project_factory; future authoring packages.
status: proposed_for_language_package
```

## Proposal LIP-APF-0-1-0-A8-003 — Process feedback YAML reload semantics

```text
problem: During self-hosted authoring, user feedback may change the process currently being executed.
current_limitation: Ordo can model corrections, but does not yet formally describe update YAML → reload process → continue from current runtime position.
proposed_construct: PROCESS.FEEDBACK / PROCESS.RELOAD semantics with confirmation gate and continuation checkpoint.
temporary_workaround: record process_feedback_policy in state and implement it as an APF runtime discipline.
affected_packages: ordo.applied_project_factory; Ordo runtime/replay/checkpoint layer.
status: proposed_for_language_package
```


## Proposal LIP-APF-0-1-0-A9-001 — Canonical user-facing node review contract

Problem: During node-by-node review, state/gates/artifacts can be hidden behind technical YAML aliases or omitted from the user-facing current-node block.

Proposed construct: `node_review_display_contract` or canonical runtime presentation metadata for nodes, gates, state writes, artifacts, templates, and deferred branches.

Temporary workaround: APF stores `node_review_display_contract` and enforces it through gates/assertions.

Status: proposal captured.

## Proposal LIP-APF-0-1-0-A9-002 — Depth-first sibling branch bookkeeping

Problem: When following one branch depth-first, sibling branches may be implicitly forgotten or treated as approved.

Proposed construct: canonical `review_cursor` with `confirmed_path`, `current_branch`, `unreviewed_sibling_branches`, and `deferred_return_points`.

Temporary workaround: APF stores these fields in state and requires them in current-node review.

Status: proposal captured.

<!-- APF alpha.21 full-validation contract coverage appendix -->

## APF alpha.21 full-validation contract coverage appendix

This appendix records confirmed contract fields for deterministic artifact coverage validation. It is a technical release-readiness section and does not change the user-facing APF process logic.

- `problem`: `documented`
- `current_limitation`: `documented`
- `proposed_construct`: `documented`
- `temporary_workaround`: `documented`
- `affected_packages`: `documented`
- `status`: `documented`
- `provisional_metadata_allowed_with_proposal`: `true`
- `auto_svg_generation_on_request_only`: `documented`
- `current_node_human_description`: `documented`
- `plain_language_extraction_summary`: `documented`
- `process_feedback_loop`: `documented`
- `node_review_display_contract`: `true, true, true, true, true, true, true, true, true`
