# 021. Process Quality Contract

## 1. Призначення

Цей документ визначає канонічний контракт оцінювання **якості процесу benchmark run**. Він оцінює те, як виконавець і Driver пройшли RUN, а не якість змісту Passport, Jira, Manual QA чи Automation artifacts.

## 2. Межа оцінювання

### In scope

- правильність Driver binding і маршруту;
- дотримання disclosure contract;
- state/evidence discipline;
- обробка corrections, withdrawal, supersession та invalidation;
- version-bound approvals;
- правильність terminal route;
- blind isolation і відсутність contamination;
- повнота execution evidence package.

### Out of scope

- якість окремих generated documents;
- стилістика або повнота Passport/Jira/QA/Automation;
- доменна правильність evaluator reference answer;
- швидкість/вартість моделі, якщо це не окремий metric profile.

## 3. Scoring model

Process score має шкалу `0..100` і складається з восьми dimensions.

| ID | Dimension | Weight | Основне питання |
|---|---|---:|---|
| `PQ-01` | Preflight and binding integrity | 10 | Чи запуск почався лише після валідного package/RUN/Driver binding? |
| `PQ-02` | Route and obligation coverage | 20 | Чи пройдений правильний route та всі mandatory obligations? |
| `PQ-03` | Evidence and state discipline | 15 | Чи кожне рішення спирається на disclosed evidence і зафіксований state? |
| `PQ-04` | Correction and invalidation handling | 15 | Чи corrections відкликали залежні facts/artifacts і запустили regeneration? |
| `PQ-05` | Approval and version control | 10 | Чи approvals прив'язані до актуальної artifact version? |
| `PQ-06` | Terminal decision correctness | 15 | Чи terminal відповідає RUN contract і фактичному стану? |
| `PQ-07` | Blind isolation and contamination control | 10 | Чи виконавець не отримав evaluator-only або historical result data? |
| `PQ-08` | Evidence package completeness | 5 | Чи достатньо evidence для незалежного повторного audit? |

Сума weights дорівнює 100.

## 4. Criterion scoring

Кожен dimension оцінюється через atomic criteria. Допустимі стани:

- `met = 1.0`;
- `partially_met = 0.5`;
- `not_met = 0.0`;
- `not_applicable` — weight перерозподіляється лише всередині dimension за явним правилом contract version.

Raw score:

```text
raw_process_score = Σ(dimension_weight × normalized_dimension_result)
```

Після raw score застосовуються failure caps із `022_PROCESS_FAILURE_CAPS.md`:

```text
final_process_score = min(raw_process_score, lowest_applicable_cap)
```

Якщо cap не застосовано, `final_process_score = raw_process_score`.

## 5. Canonical criteria

### PQ-01. Preflight and binding integrity

- checksums та package identity перевірені;
- RUN contract існує і version pinned;
- Driver selected до execution;
- blind isolation manifest пройшов gate;
- residue check пройдено або run позначено contaminated до execution.

### PQ-02. Route and obligation coverage

- route відповідає selected Driver family;
- mandatory nodes/obligations не пропущені;
- executor не завершив run перед terminal gate;
- question batching не приховало mandatory obligation;
- unsupported/hybrid package не був довільно виконаний.

### PQ-03. Evidence and state discipline

- facts мають status і provenance;
- Driver не розкриває hidden facts без trigger;
- state transitions записані append-only;
- рішення не базуються на assumptions, виданих за confirmed facts;
- generated artifact versions простежуються до active facts.

### PQ-04. Correction and invalidation handling

- correction/withdrawal/supersession зафіксовані;
- affected facts змінюють status;
- залежні artifacts/approvals invalidated;
- regeneration або revalidation виконані;
- stale version не використана для terminal decision.

Для RUN без corrections criterion має статус `not_applicable` за contract rule, а dimension оцінює готовність механізму через відсутність неправомірних invalidations.

### PQ-05. Approval and version control

- approval містить artifact ID/version/hash;
- approval не переноситься на regenerated version;
- terminal використовує останню approved або allowed unapproved version за RUN contract;
- approvals і invalidations відображені в log.

### PQ-06. Terminal decision correctness

- terminal route входить до allowed terminal set RUN contract;
- `T_COMPLETED` не використано при missing blocking input;
- `T_INPUT_BLOCKED` містить конкретний blocker;
- `T_SCENARIO_EXHAUSTED` використано лише після вичерпання relevant evidence;
- `T_NOT_READY` і `T_NO_GO` не підмінюють один одного;
- terminal disposition узгоджений із execution log.

### PQ-07. Blind isolation and contamination control

- evaluator-only files не були executor-visible;
- reference outputs/scores/caps не передавались виконавцю;
- previous results/diagnostics не використовувались;
- contamination event зафіксований, якщо isolation порушено;
- contaminated run не позначений clean blind run.

### PQ-08. Evidence package completeness

Мінімально присутні:

- launch manifest;
- preflight report;
- Driver binding/isolation records;
- append-only execution log;
- artifact inventory/version map;
- terminal disposition;
- evaluator process report.

## 6. Evaluation sequence

1. Pin `process_quality_contract_version`.
2. Перевірити integrity evidence.
3. Відновити фактичний route з execution log.
4. Оцінити criteria без перегляду document-quality scores.
5. Обчислити raw score.
6. Визначити applicable failures і caps.
7. Застосувати найнижчий cap.
8. Записати evidence references для кожного criterion.
9. Зафіксувати uncertainty та non-scorable gaps.

## 7. Evidence rule

Жоден criterion не може отримати `met` лише на основі narrative summary. Потрібне посилання на immutable evidence: event sequence, artifact hash/version, manifest field або terminal record.

Відсутність evidence оцінюється як `not_met`, якщо criterion мав бути доказовим. Не дозволено припускати, що дія відбулася.

## 8. Output contract

Результат оцінювання має відповідати:

- `templates/PROCESS_EVALUATION_REPORT.template.json`;
- `schemas/process_evaluation_report.schema.json`;
- `PROCESS_FAILURE_CAPS.yaml`.

Обов'язкові поля: attempt identity, contract versions, criterion results, raw score, detected failures, applied cap, final score, evidence references, uncertainty, evaluator identity/time.

## 9. Gate

Process evaluation валідна, якщо:

- weights = 100;
- усі applicable criteria мають evidence/status;
- raw score відтворюваний;
- caps застосовані після raw score;
- lowest applicable cap використано;
- document scores не змішані з process score;
- contaminated run явно позначений.

## 10. Readiness

Цей контракт визначає evaluation semantics. Він не є production evaluator executable і не заявляє автоматичне обчислення без майбутнього runner-а.
