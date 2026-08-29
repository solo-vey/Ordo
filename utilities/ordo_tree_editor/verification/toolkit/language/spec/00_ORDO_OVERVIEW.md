# 00. Ordo Overview

Ordo — це AI-first мова Process Rail для керування складною роботою AI-агентів. Вона описує процес не як довгий prompt і не як жорсткий wizard, а як керований execution contract:

```text
intent → contract → context → state → path → steps → gates → result → handoff
```


## M26 — Process Rail Reframing

M26 уточнює ядро Ordo: Ordo є AI-guided process language, а не CLI-first runtime. Центральна модель — **Process Rail**.

```text
AI thinks and speaks.
Process Rail keeps the process aligned.
CLI validates deterministic parts.
Semantic JSON IR is the machine-readable form of the rail.
```

Process Rail дозволяє ШІ вести гнучкий діалог, але тримає state, route, gates, deviation handling, backtracking і output readiness.

## M27 — Project Builder

M27 додає AI-guided authoring: PM описує задачу природною мовою, а AI Ordo Developer створює Ordo YAML, запускає helper checks і компілює Semantic JSON IR.

## M28 — Hybrid Execution

M28 додає AI-led execution: AI Ordo Executor виконує готовий Semantic JSON IR як Process Rail, класифікує людський input, оновлює state, викликає deterministic helper checks і пояснює людині наступний крок. CLI не стає головним conversational runtime.

## M30 — Alignment note

Після M30 основний спосіб читати Ordo такий:

```text
AI remains the active cognitive executor.
Process Rail keeps the work aligned.
Semantic JSON IR stores the machine-readable rail.
CLI helper tools validate deterministic parts.
```

Тому старі формулювання на кшталт “CLI виконує процес” треба читати як скорочення: CLI допомагає перевіряти й стабілізувати процес, але людський діалог веде AI.

## v0.12 reliability principle

У v0.12 Ordo додає явну семантику довіри. Кожна критична дія має бути зрозумілою не тільки за змістом, а й за способом контролю:

```text
what is checked → who checks it → by which method → with which trust class → under which execution mode
```

## Main language layers

```text
Ordo Core
Ordo Profiles
Domain Packs
Libraries
Controlled FREEFORM
Debug/Test/Improvement Layer
Reliability/Trust Semantics
```

## Canonical execution object

Мінімальна Ordo-програма v0.12 має явно вказувати:

```yaml
program:
  id: example.program
  ordo_version: "0.12"
  control_level: standard
  execution_mode: chat_internal
```

Для `strict`-режиму додатково потрібні debug/test/reliability coverage.

## M64.3 Program-level approval gate model

M64.3 adds `18_PROGRAM_LEVEL_APPROVAL_GATE_MODEL.md` as a docs/lint-profile design chapter. It defines how top-level M64 package contracts can be reviewed with severity levels and light/standard/strict profiles. It does not add runtime semantics or opcodes.
