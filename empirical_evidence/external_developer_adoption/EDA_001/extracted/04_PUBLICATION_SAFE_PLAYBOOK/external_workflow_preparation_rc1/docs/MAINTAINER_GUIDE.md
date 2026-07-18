# Maintainer Guide

The graph separates business runtime state from work-tracking system workflow status. Corrections backtrack to the earliest affected node and invalidate dependent artifacts/sign-offs.

External systems are non-mutating: outputs are copy-ready Markdown. Only the external process record URL and Workflow Preparation work-tracking system URL are mandatory. URL checks are limited to non-empty URL-shaped values; no host allowlist or remote accessibility check is performed.

Draft publication requires explicit analyst approval. Link synchronization does not require a second approval if deterministic checks prove business content is unchanged.

Approver handling is combined: the model proposes a minimum set based on data mode, Product/PO confirms or edits it, and each human approver records their own decision. The model can never approve.

Temporary runtime evidence and personal sign-off working data are removed after process completion. The final package remains durable. Every future version bump requires a verified immutable rollback checkpoint and disposable restore round-trip.


Lifecycle link placement is intentionally narrow: external documentation system URL only in the work-tracking record document; Workflow Preparation work-tracking system URL only in README.md. Duplicate placement is a validation error.
