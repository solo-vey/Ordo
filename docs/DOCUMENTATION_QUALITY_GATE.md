# Documentation quality gate

The documentation quality gate protects the active user-facing documentation contour without rewriting historical or immutable evidence.

It verifies:

- canonical front-door documents exist;
- relative file links and local heading anchors resolve;
- the root README prioritizes chat-first onboarding;
- the starter ZIP is reproducible from its declared source files;
- README, citation, backlog maturity, release identity, and version state use the same packaged release versions;
- optional CLI instructions remain available without becoming the primary onboarding route;
- historical broken-link exceptions are exact, documented, and do not expand through broad globs.

The machine-readable policy is [`../manifests/DOCUMENTATION_QUALITY_GATE.json`](../manifests/DOCUMENTATION_QUALITY_GATE.json).

External URLs are not dereferenced by the offline gate. Historical archives, immutable evidence, and compiled legacy books retain their original bytes unless a separately authorized migration changes them.
