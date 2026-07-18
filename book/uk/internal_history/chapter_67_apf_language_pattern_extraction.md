# Розділ 67. APF Language Pattern Extraction

M62.3 не додає новий runtime і не переписує APF. Його задача інша: взяти ідеї, які виникли під час review `ordo.applied_project_factory`, і розкласти їх по рівнях зрілості.

Головне правило: якщо APF потребує певний патерн, це ще не означає, що він одразу має стати op-code або IR-обʼєктом.

Правильна драбина така:

```text
потреба APF
→ документований APF-патерн
→ reusable APF subflow або state convention
→ використання в кількох пакетах
→ lint/check candidate
→ formal language construct
→ IR/runtime object тільки якщо справді потрібно
```

## Чому це важливо

Під час створення прикладних процесів легко захотіти формалізувати все одразу:

```text
INPUT.POLICY
TERMINAL.OUTPUT.BIND
TREE.AUTHOR.PROGRESSIVE
NODE.REVIEW
FLOW.JOIN
```

Але частина цих речей — це user-facing authoring workflow. Частина — schema convention. Частина — майбутні lint rules. І лише дуже мала частина може колись стати IR-level конструкцією.

## Поточна класифікація

M62.3 класифікує APF-кандидати так:

```text
Documentation pattern
APF reusable subflow
Schema convention
Artifact standard
Rendering standard
Package authoring policy
Lint candidate
Future IR candidate
```

Найближчі практичні кандидати для APF patch — це input policy, output candidate catalog, progressive tree authoring, node/branch review, terminal output binding і terminal readiness check.

Найсильніші майбутні IR-кандидати — `FLOW.JOIN` і `SHARED.TAIL.REFERENCE`, але вони потребують окремого design milestone.

## Межа M62.3

M62.3 не робить:

```text
APF YAML rewrite
нові opcodes
runtime-core зміни
execution/scoring/calibration
watchdog/process-boundary hardening
```

Це тільки план вилучення мовних патернів із APF-досвіду.

## Наступна здорова межа

Після M62.3 варто зробити M62 Line Closure і зафіксувати:

```text
M62.1 — APF imported
M62.2 — APF documented
M62.3 — APF patterns classified
```

А вже потім відкривати окрему M63-лінію для продовження branch review і scoped YAML patch.
