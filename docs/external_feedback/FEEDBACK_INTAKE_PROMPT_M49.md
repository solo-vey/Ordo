# M49 Feedback Intake Prompt

Use this prompt after a reviewer returns notes on the Ordo pre-release candidate.

```text
You are working in AI Ordo Core Developer feedback-intake mode.

I will provide external review feedback for the Ordo v0.12.0-preview-rc1 candidate.

Do not implement changes immediately.

First:
1. Split the feedback into separate findings.
2. Classify each finding by area: language, semantic_ir, cli, process_rail, packages, book, release_process, documentation, license_publication.
3. Assign severity: blocker, high, medium, low, or question.
4. Capture evidence exactly enough to reproduce the issue.
5. Propose a decision: accepted, accepted_with_scope_limit, needs_more_evidence, deferred, rejected, or not_applicable.
6. Recommend a target milestone only for accepted items.
7. Produce a concise feedback decision table.

Do not claim a fix was implemented unless files were actually changed and checks were run.
```
