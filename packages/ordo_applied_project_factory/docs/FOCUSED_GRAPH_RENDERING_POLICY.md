# Focused Graph Rendering Policy

Status: APF v0.1.0-alpha.8 confirmed policy.

## Rule

When the AI Ordo Project Factory Developer is working with a specific part of a decision tree, the default SVG view is **context view**:

```text
root path → current node → full subtree below current node
```

## Why

Full-tree diagrams become noisy during branch-level authoring. The user needs to see the path currently being reviewed, the current node, and the downstream alternatives that are affected by the current decision.

## Rendering modes

```text
context: default during branch work
subtree: downstream debugging only
path: navigation-only explanation
full tree: overview/release review only
```

## Future project instruction

Generated applied projects should inherit this policy. If a user is reviewing a branch, generated graph artifacts should prefer context SVG and include full-tree SVG only as an optional overview.

## Required fields

```text
context_view_default: true
root_to_current_node: true
current_subtree: true
full_tree_overview_only: true
future_project_instruction: inherit policy in generated applied projects
```

## Runtime generation rule

During ordinary node-by-node text review, SVG is **not** generated automatically.

Generate SVG only when the user explicitly asks for it. When requested, use context view by default:

```text
root path → current node → full subtree below current node
```

Required fields added in APF v0.1.0-alpha.8:

```text
auto_svg_generation_on_request_only: true
current_node_human_description: true
plain_language_extraction_summary: true
process_feedback_loop: true
```

<!-- APF alpha.21 full-validation contract coverage appendix -->

## APF alpha.21 full-validation contract coverage appendix

This appendix records confirmed contract fields for deterministic artifact coverage validation. It is a technical release-readiness section and does not change the user-facing APF process logic.

- `context_view_default`: `documented`
- `root_to_current_node`: `documented`
- `current_subtree`: `documented`
- `future_project_instruction`: `documented`
- `auto_svg_generation_on_request_only`: `documented`
- `current_node_human_description`: `documented`
- `plain_language_extraction_summary`: `documented`
- `process_feedback_loop`: `documented`
