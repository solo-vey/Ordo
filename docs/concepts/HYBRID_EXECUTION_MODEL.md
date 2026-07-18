# Hybrid Execution Model

Hybrid Execution Model describes how a ready Ordo package is executed by an AI Ordo Executor.

## Core idea

```text
Human message
  ↓
AI Ordo Executor interprets intent
  ↓
Process Rail maps the message to state/path/gates
  ↓
Deterministic helper checks the mechanical parts
  ↓
AI explains the result and chooses the next move
```

## What AI does

- understands natural language;
- asks clarifying questions;
- detects corrections and changed decisions;
- explains process state to the human;
- decides how to resume the process after deviation;
- generates outputs only after gates allow it.

## What deterministic helpers do

- validate state completeness;
- check gate status;
- suggest next step candidates;
- detect missing required fields;
- validate whether output generation is allowed;
- provide machine-readable feedback to the AI.

## Human-facing rule

Raw tool output is not the user interface. The AI Ordo Executor interprets helper results and explains them in human language.

## Non-goal

M28 does not turn CLI into a full deterministic conversational runtime. CLI supports execution but does not replace AI-led execution.
