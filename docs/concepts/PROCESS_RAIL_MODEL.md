# Process Rail Model

## In brief

**Process Rail** is a supporting process structure for AI. It lets AI conduct a
flexible conversation with a person while retaining state, route, gates,
required decisions, backtracking, and output rules.

Ordo does not replace AI with a deterministic wizard. Ordo gives AI rails.

```text
AI thinks and speaks.
Process Rail keeps the process aligned.
Deterministic helper tools validate what can be validated.
```

## Problem

- A prompt-only approach is flexible, but the model can skip a step, forget a
  previous decision, or lose its place after backtracking.
- A hardcoded wizard is stable, but handles open answers, clarification,
  changed decisions, and domain reasoning poorly.
- Ordo provides an intermediate option: a live AI conversation stabilised by a
  formal Process Rail.

## Main Process Rail components

- `rail_state` — current traversal state.
- `rail_node` — current or available process node.
- `required_checkpoints` — required points that cannot be skipped.
- `gates` — formal checks allowing further movement or output generation.
- `deviation_policy` — what to do if a person leaves the current question.
- `backtracking_policy` — how to return to a previous decision.
- `resume_policy` — how to return to the main route after a deviation.

## AI role

AI remains the main active element. It:

- interprets natural language;
- asks clarifying questions;
- advises and warns about risks;
- proposes decisions;
- explains process state;
- turns technical tool results into a human explanation.

## CLI role

The CLI does not conduct a conversation with a person. It helps AI to:

- validate syntax;
- compile Ordo source into Semantic JSON IR;
- validate state/gates;
- find missing fields;
- compare state/IR;
- run deterministic checks.

Raw CLI output is not shown to a person unnecessarily. AI interprets it.

## Two scenarios

### AI-guided authoring

A PM describes a task in natural language. The AI Ordo Developer designs an
Ordo project, creates YAML, runs lint/compile, and explains its state to the
PM.

### Hybrid execution

A user traverses a completed Ordo project. The AI Ordo Executor reads Semantic
JSON IR, conducts the conversation, handles deviations, and uses the CLI as a
deterministic helper.

## Definition of Done

The Process Rail model is considered established when:

- Ordo is not described as a CLI-first runtime;
- AI explicitly remains the active cognitive executor;
- the CLI is positioned as a helper/checker;
- Semantic JSON IR contains Process Rail semantics;
- backtracking/deviation/resume are described as parts of the language.
