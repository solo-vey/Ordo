# CLI as Deterministic Helper

In M26, the CLI is positioned as a deterministic helper layer.

The CLI is not the primary conversational runtime. AI is the primary active
actor.

The CLI helps AI to:

- validate Ordo package syntax;
- compile source YAML into Semantic JSON IR;
- run tests and coverage;
- check deterministic gates;
- identify missing fields or inconsistencies;
- produce machine-readable diagnostics.

Raw CLI output is intended for AI/developer interpretation by default. AI must
produce the human-facing response in plain language.
