# CLI in Ordo Project Authoring

У Project Builder сценарії CLI не є співрозмовником PM.

CLI виконує роль deterministic helper layer для AI Ordo Developer:

- `ordo lint` перевіряє синтаксис і базові правила;
- `ordo compile` створює Semantic JSON IR;
- `ordo test` перевіряє очікувані gates/assertions;
- `ordo coverage` показує покриття nodes/gates/tests;
- `ordo validate-artifacts` перевіряє, що підтверджені contract values реально потрапили у rendered artifacts.

AI Ordo Developer має прочитати результат CLI і пояснити PM-у зміст людською мовою.

```text
CLI output → AI interpretation → PM-facing explanation
```
