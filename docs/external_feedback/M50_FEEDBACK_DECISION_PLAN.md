# M50 — Feedback Decision / Post-Review Change Planning

Status: `planning-ready`
Target: `v0.12.0-preview-rc1`
Scope: no new language semantics, CLI runtime behavior, or package business logic.

M50 converts reviewer feedback intake into a repeatable decision route. It does not apply product changes by itself. It decides what should be accepted, deferred, rejected, or converted into a future milestone.

## Purpose

After M49, Ordo can collect external review feedback. M50 defines how that feedback becomes a controlled change plan without breaking the frozen release candidate.

The route is:

```text
review item
→ classify
→ decide
→ assign target milestone
→ define acceptance criteria
→ run self-check after implementation
```

## Decision statuses

```text
accepted_now
accepted_next_milestone
deferred
rejected
needs_reproduction
needs_owner_decision
```

## Severity levels

```text
blocker
critical
high
medium
low
note
```

## Decision rules

- `blocker` or `critical` feedback must be resolved before public preview publication.
- `high` feedback must be either accepted into the next milestone or explicitly deferred with rationale.
- `medium` feedback can be batched into a planned improvement milestone.
- `low` and `note` feedback can be tracked as backlog unless they reveal a trust or release-integrity issue.
- Any finding that contradicts validation evidence must become a release-quality task, not a documentation-only task.

## Required fields for each decision

```yaml
feedback_id: <id>
source: external_review | self_audit | user_test | regression
severity: blocker | critical | high | medium | low | note
decision: accepted_now | accepted_next_milestone | deferred | rejected | needs_reproduction | needs_owner_decision
target_milestone: M51 | later | none
rationale: <short reason>
acceptance_criteria:
  - <criterion>
validation_commands:
  - <command>
```

## M50 output

M50 creates decision templates and a post-review change plan. It does not modify runtime behavior.
