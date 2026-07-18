# ASR-3 — Review Flow Integration and Decomposition Proposal

Status: completed

Atomic Step Review is now positioned after a step contract is drafted and before step confirmation, prompt sufficiency review, final trace-event mapping, and package assembly.

Implemented:

- canonical review flow and transition rules;
- blocking/pause behavior for unresolved findings;
- structured minimal-safe-split proposal;
- explicit human-decision boundary;
- mandatory re-review after an approved decomposition;
- integration rules with prompt, trace, artifact validation, and package assembly layers.

No automatic rewrite of confirmed business logic was introduced.
