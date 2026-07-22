# AI-guided Authoring and Hybrid Execution

## 1. AI-guided authoring

An analyst or PM does not write Ordo YAML manually. They describe the domain,
goal, and rules in natural language.

**AI Ordo Developer**:

- studies the requirement;
- asks clarifying questions;
- proposes a process structure;
- creates or updates Ordo YAML;
- runs deterministic checks through the CLI;
- compiles the project into Semantic JSON IR;
- explains issues, gaps, and next decisions to the PM in plain language.

Authoring cycle:

```text
PM answer → AI analysis → YAML update → lint/compile → AI explanation → next PM decision
```

## 2. Hybrid execution

A completed Ordo project is not executed as a rigid Python wizard. It is
executed by an **AI Ordo Executor** that follows the Process Rail in Semantic
JSON IR.

Execution cycle:

```text
Human input → AI interpretation → proposed state update → deterministic helper check → AI explanation → next move
```

## 3. Raw tool output policy

Deterministic tools can return JSON, reports, or diagnostics. By default this
is machine-facing feedback for AI, not a response for a person.

The person receives an explanation:

```text
not: {"missing": ["event_alias"]}
but: A short technical alias for the event is still missing.
```

## 4. Proactive AI behavior

An AI Ordo Developer and AI Ordo Executor are not passive coders. They must:

- identify contradictions;
- warn about risks;
- propose options;
- explain the consequences of a choice;
- request a decision where a deterministic rail cannot choose on its own.
