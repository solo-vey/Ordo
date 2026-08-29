# Process Pattern Engineering Model

`PATTERN.DEF` is a stable optional first-class governance construct for positive reusable process patterns.

A pattern definition MUST declare identity, lifecycle status, intent, applicability requirements and exclusions, ordered steps, composition constraints, evidence requirements, review template, and provenance.

Recommendation is fail-closed: a pattern is recommendable only when every declared requirement is present, no exclusion is active, and status is `validated` or `stable`.

Composition is permitted only through an explicitly declared `may_precede` or `may_follow` relation. Pattern composition never overrides blocking gates, protected state, authority boundaries, or package-specific contracts.

Promotion to `stable` requires evidence from at least two real canonical packages plus human approval. A generated review card remains `blocked` while any required evidence is missing.
