# Branch 1 Progressive Tree Authoring Policy

APF `v0.1.0-alpha.15` closes human review for branch 1: **Доменна модель + дерево рішень**.

## Main decisions

1. `runtime_entry_point` is not asked immediately after roles. It is resolved after domain model, input policy, output catalog and open questions.
2. Input artifacts are policy-based, not mandatory. Supported statuses: required, optional, no predefined input, unknown/deferred, or produced later.
3. Output artifacts are separated from output templates. At first the user may only provide a candidate list, ask AI to propose outputs, or defer outputs.
4. Terminal points perform output binding: select outputs from a candidate catalog, add a new output, explicitly set no-output, or defer output selection.
5. Every selected non-deferred output needs a verified template or accepted alpha-template and a mock-filled example before terminal path readiness.
6. Static decision-tree blueprint is replaced with progressive authoring. The user may describe a root and first branches, a deeper subtree, a full draft, or free-form logic.
7. Every reviewed branch must pass a terminal-or-continue decision.
8. Subtree closure must check unreviewed siblings, deferred return points, correction items, blocking open questions and terminal output binding status.

## Shared status

The full-validation / handoff tail is shared. Branch 1 does not duplicate it.
