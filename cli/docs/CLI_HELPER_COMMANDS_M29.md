# M29 — CLI helper commands alignment

## Purpose

The Ordo CLI is a deterministic helper layer for AI-guided Ordo work. It is not the primary conversational runtime and it should not speak directly to the PM/user as the main process actor.

AI remains responsible for interpretation, advice, explanation and the next conversational move. The CLI provides stable machine-readable checks.

## Added helper commands

```bash
ordo validate-state <package> [--state state.yaml] [--answers answers.yaml]
ordo check-gate <package> <gate_id> [--state state.yaml] [--answers answers.yaml]
ordo next-step <package> [--state state.yaml] [--answers answers.yaml]
ordo diff-state <package> --before old_state.yaml --after new_state.yaml
ordo explain-validation <package> [--report reports/state_validation_report.json]
```

## Human-output policy

Raw CLI output is helper evidence. AI Ordo Developer / AI Ordo Executor must interpret it before showing a human-facing answer.

```text
CLI says: missing_required_fields=[project_domain]
AI says: Нам ще потрібно визначити домен проєкту. Без цього я не можу стабільно зібрати Ordo-проєкт.
```

## Scope

M29 aligns the CLI with the Process Rail model. It does not make the CLI a full dialogue wizard and does not replace AI-led authoring or execution.
