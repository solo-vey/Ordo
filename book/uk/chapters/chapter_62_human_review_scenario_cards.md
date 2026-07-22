# Розділ 62. Human Review Scenario Cards

M61.0 додає до PathWalk проміжний шар між згенерованими real-module testcase artifacts і майбутнім runtime execution.

Його задача проста: зробити так, щоб QA, developer або reviewer могли швидко прочитати згенерований кейс як сценарну картку, а не розбирати сирий JSON.

## Що було до цього

Після M60.7 маємо artifact-only ланцюжок:

```text
source/program.ordo.yaml
→ REAL_MODULE_GRAPH_SUMMARY.json
→ REAL_MODULE_TERMINAL_PATHS.json
→ clean path cases
→ bounded noise cases
```

Clean/noise cases уже структуровані, але вони більше схожі на машинні artifacts.

M61.0 додає людський шар:

```text
clean path cases + bounded noise cases
→ human review scenario cards
```

## Команда

```bash
PYTHONPATH=cli:. python3 -m utilities.ordo_pathwalk.cli real-module-review-cards \
  --summary runs/real_module_clean_cases/SUMMARY.json \
  --summary runs/real_module_noise_cases/SUMMARY.json \
  --out runs/real_module_review_cards \
  --force
```

## Artifacts

Команда створює:

```text
cards/<card_id>.json
cards/<card_id>.md
REVIEW_CARDS.json
REVIEW_CARDS.md
RAW_REVIEW_CARD_MATRIX.csv
VALIDATION_REPORT.json
```

`cards/*.md` — це основний формат для людини. Там видно:

- case id;
- path id;
- noise pattern;
- scripted steps;
- expected behavior;
- expected terminal;
- expected outputs;
- review checklist.

## Що це не робить

M61.0 не запускає runtime.

Він також не робить:

- model/API benchmark;
- scoring;
- calibration;
- watchdog/process-boundary hardening;
- runtime-harness matrix.

Це важлива межа, щоб не повернутися до blocked гілки M60.6.5 / M60.6.4.1.

## Readiness

У review-card artifacts readiness розділена явно:

```text
review_cards_ready      # ціль M61.0
runtime_execution_ready # false
scoring_ready           # false
calibration_ready       # false
```

Тобто картки готові для людського ревʼю, але не є доказом runtime проходження або якості моделі.

## Чому це корисно

Human review cards дають практичну користь без важкого execution infrastructure:

- можна руками переглянути coverage terminal paths;
- можна побачити, як виглядає distraction / invalid_branch / clarification / skip_ahead;
- можна використати картки як QA checklist;
- можна підготуватися до майбутнього runtime execution milestone.

## Межа зупинки

M61.0 — це правильний наступний шар після M60.8 handoff, бо він підвищує usability без відкриття runtime orchestration.

Наступні речі лишаються future work:

```text
M62.0 Runtime Execution of Generated Testcases
backtrack
correction_backtrack
scoring generated cases
calibration generated cases
watchdog/process-boundary hardening
```
