# Ordo v0.12.0-preview — Release Candidate Freeze

## Status

Release candidate freeze for `v0.12.0-preview`.

This freeze keeps the M26–M35 direction intact:

- Ordo is Process Rail centered.
- AI remains the active cognitive executor.
- CLI is a deterministic helper layer, not the primary conversational runtime.
- `ordo_project_builder` demonstrates AI-guided authoring.
- `ordo_hybrid_executor` demonstrates AI-led execution over Semantic JSON IR.
- Publication mode remains source-available preview candidate until the license decision is finalized.

## Freeze rule

No new conceptual scope is introduced in M36. Changes are limited to release-candidate review, validation evidence, and publication readiness notes.

## Reviewer focus

Reviewers should check:

1. Whether Process Rail is understandable from `README.md`.
2. Whether the Authoring and Hybrid Execution packages make the core model concrete.
3. Whether CLI helper commands are positioned as AI support tools, not as a wizard runtime.
4. Whether the license/publication mode is clear enough for preview sharing.
5. Whether the package is safe to publish as a preview candidate after external review.


## M37 review handoff note

M37 does not change the release-candidate feature scope. It adds `docs/review_handoff/` as the recommended external review route for `v0.12.0-preview`.
