# 12. Project Builder Model

## 1. Статус

**Ordo language line:** v0.12  
**Milestone:** M27 — Ordo Project Builder  
**Статус:** conceptual package model

## 2. Призначення

Project Builder Model описує, як створювати Ordo-проєкти через діалог PM з AI Ordo Developer.

Цей режим відрізняється від execution mode. У ньому предметом роботи є сам Ordo-проєкт: його Process Rail, state schema, nodes, gates, outputs і Semantic JSON IR.

## 3. Базова формула

```text
PM intent → AI Ordo Developer → Ordo YAML → helper checks → Semantic JSON IR → PM-facing explanation
```

## 4. Основні правила

- PM не зобов'язаний писати YAML.
- AI Ordo Developer має активно уточнювати, радити і виявляти прогалини.
- Після зміни YAML має виконуватися lint/compile або інший доступний deterministic check.
- Raw tool output не передається PM напряму без AI-інтерпретації.
- Semantic JSON IR є контрольованим результатом authoring loop.

## 5. Мінімальні authoring fields

```yaml
project_authoring:
  human_role: pm
  ai_role: ordo_developer
  project_goal: required
  project_domain: required
  process_rail_goal: required
  state_model_summary: required
  required_outputs: required
  deterministic_helper_scope: required
```

## 6. Reference package

M27 додає reference package:

```text
packages/ordo_project_builder/
```
