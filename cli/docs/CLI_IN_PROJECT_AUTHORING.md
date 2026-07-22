# CLI in Ordo Project Authoring

In the Project Builder scenario, the CLI is not the PM's conversational
counterpart.

The CLI acts as a deterministic helper layer for an AI Ordo Developer:

- `ordo lint` validates syntax and basic rules;
- `ordo compile` creates Semantic JSON IR;
- `ordo test` validates expected gates/assertions;
- `ordo coverage` shows node/gate/test coverage;
- `ordo validate-artifacts` verifies that confirmed contract values appear in
  rendered artifacts.

The AI Ordo Developer must read the CLI result and explain its meaning to the
PM in plain language.

```text
CLI output → AI interpretation → PM-facing explanation
```
