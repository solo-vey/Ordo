# Ordo Project Builder

`Ordo Project Builder` is an authoring mechanism for creating new Ordo
projects through a conversation between a PM and an AI Ordo Developer.

## Core idea

A PM does not write Ordo code directly. The PM explains the required process,
domain, or analytical product. The AI Ordo Developer turns these explanations
into Ordo YAML, validates it through the CLI, and compiles it into Semantic
JSON IR.

## Loop

```text
PM explains the intent
  ↓
AI Ordo Developer clarifies and proposes a solution
  ↓
AI updates Ordo YAML
  ↓
CLI helper checks syntax / gates / compilation
  ↓
AI explains the state to the PM in plain language
  ↓
PM confirms, changes, or adds information
```

## AI Ordo Developer role

An AI Ordo Developer is not a passive coder. It must:

- identify gaps;
- propose a Process Rail structure;
- advise on gates and state;
- explain the consequences of PM decisions;
- keep YAML and Semantic JSON IR valid;
- not show raw CLI output without interpretation.

## Result

An authoring session results in an Ordo project with:

- `ordo.yml`;
- `source/program.ordo.yaml`;
- tests;
- output templates, if needed;
- compiled Semantic JSON IR;
- an understandable PM-facing summary.
