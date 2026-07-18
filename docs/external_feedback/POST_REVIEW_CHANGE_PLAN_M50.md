# Post-Review Change Plan — M50

Status: `ready_for_feedback_items`

No external feedback items have been accepted into implementation in this milestone. This plan defines the queue used after reviewers return findings.

## Change queue

| Priority | Type | Rule |
|---|---|---|
| P0 | release blocker | Must be fixed before publication. |
| P1 | trust/validation issue | Must be fixed or explicitly deferred before publication. |
| P2 | usability issue | Can be scheduled into the next implementation milestone. |
| P3 | documentation issue | Can be fixed in docs-only milestone. |
| P4 | idea/backlog | Track for later. |

## Default next milestone mapping

```text
P0/P1 → M51 hotfix or release-blocker fix
P2    → M52 usability improvement
P3    → M53 documentation alignment
P4    → backlog
```

## Required implementation loop

For every accepted item:

```text
1. reproduce or confirm
2. identify affected layer
3. apply minimal change
4. add regression check if applicable
5. update docs/book markdown if user-facing behavior changes
6. run self-check
7. record decision and validation evidence
```

## Affected layers

```text
language
semantic_ir
cli
reference_package
docs
book_md
release_evidence
developer_bundle
```

## Current decision

The current package remains a release candidate until real external feedback is supplied and classified.
