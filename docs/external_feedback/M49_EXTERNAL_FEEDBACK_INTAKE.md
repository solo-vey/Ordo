# M49 — External Feedback Intake

M49 defines how feedback from external review is captured after the `v0.12.0-preview-rc1` handoff.

This milestone adds no new language semantics, CLI runtime behavior, or package business logic. It records the review intake path so feedback can be classified before any code or specification changes are made.

## Purpose

External feedback should not immediately become implementation work. It first becomes a structured intake item with a decision status.

```text
review finding → feedback item → triage → decision → next milestone or no action
```

## Feedback item fields

Each feedback item should include:

- `id`
- `source`
- `area`
- `severity`
- `evidence`
- `recommended_action`
- `decision`
- `owner`
- `target_milestone`

## Allowed areas

```text
language
semantic_ir
cli
process_rail
packages
book
release_process
documentation
license_publication
```

## Allowed severity

```text
blocker
high
medium
low
question
```

## Allowed decision statuses

```text
accepted
accepted_with_scope_limit
needs_more_evidence
deferred
rejected
not_applicable
```

## Rule

No post-review change should be applied directly to the release candidate without a feedback item and a decision.
