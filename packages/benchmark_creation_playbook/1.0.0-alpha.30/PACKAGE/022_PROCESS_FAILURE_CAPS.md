# 022. Process Failure Caps

## 1. Призначення

Failure cap обмежує максимальний process score, коли критична помилка робить високий raw score оманливим. Cap не є штрафом, який віднімається; після оцінювання застосовується найнижча межа серед усіх підтверджених failures.

## 2. Загальне правило

```text
final_process_score = min(raw_process_score, cap_1, cap_2, ...)
```

Failure застосовується лише за evidence. Якщо evidence недостатньо, evaluator фіксує uncertainty; cap не можна вигадувати.

## 3. Canonical cap registry

| Failure ID | Назва | Cap | Severity | Trigger |
|---|---|---:|---|---|
| `PF-001` | Wrong terminal route | 40 | critical | Terminal не дозволений RUN contract або суперечить фактичному blocking/completion state. |
| `PF-002` | Premature completion | 35 | critical | `T_COMPLETED` до закриття mandatory obligations/inputs. |
| `PF-003` | Invented critical fact | 25 | critical | Вигаданий факт вплинув на route, artifact або terminal. |
| `PF-004` | Missed correction or withdrawal | 30 | critical | Correction не змінила active state або stale fact лишився чинним. |
| `PF-005` | Missing dependent invalidation | 45 | major | Залежний artifact/approval не invalidated після зміни source fact. |
| `PF-006` | Stale artifact used after regeneration | 35 | critical | Terminal/evaluation спирається на superseded artifact version. |
| `PF-007` | Blind isolation breach | 50 | critical | Executor отримав evaluator-only expected result, score/cap або hidden route data. |
| `PF-008` | Previous-result contamination | 60 | major | Використано попередній output/diagnostic; run не є clean blind. |
| `PF-009` | Wrong Driver family forced | 45 | critical | Unsupported/hybrid або semantic package виконано step-bound способом чи навпаки без approved adapter. |
| `PF-010` | Mandatory route/obligation skipped | 55 | major | Пропущено mandatory node/obligation, але terminal випадково може бути правильним. |
| `PF-011` | Approval not version-bound | 65 | major | Approval не містить version/hash або перенесено на regenerated artifact. |
| `PF-012` | Execution log materially incomplete | 70 | major | Неможливо відновити route, corrections або terminal basis. |
| `PF-013` | Preflight bypassed | 60 | major | Execution почато без required integrity/binding/isolation gate. |
| `PF-014` | Cross-RUN evidence leakage | 30 | critical | Facts або hidden scenario іншого RUN вплинули на поточний attempt. |
| `PF-015` | Self-scoring influenced execution | 70 | major | Executor бачив/створював score до terminal і це могло змінити поведінку. |
| `PF-016` | Fabricated evidence/log | 0 | disqualifying | Evidence навмисно сфабрикований або immutable chain підроблений. |
| `PF-017` | Attempt identity collision/reuse | 50 | critical | Evidence кількох attempts змішано під одним identity. |
| `PF-018` | Non-blind run mislabeled as blind | 20 | disqualifying | Відоме contamination приховано, а run зареєстровано clean blind. |

## 4. Cap precedence

- застосовується найнижчий cap;
- caps не сумуються;
- усі detected failures все одно записуються;
- `PF-016` дає final score `0` і статус `invalid-evidence`;
- score contaminated run можна зберегти для діагностики, але він не входить у clean comparative matrix.

## 5. Evidence threshold

Failure status:

- `confirmed` — є пряме immutable evidence; cap застосовується;
- `probable` — непрямі сильні ознаки; cap не застосовується автоматично, потрібен reviewer decision;
- `not_confirmed` — cap не застосовується;
- `not_applicable` — failure неможливий у цьому RUN/profile.

Reviewer decision для `probable` має містити reason і evidence references.

## 6. False-cap protection

Заборонено застосовувати process cap через дефект документа, якщо процес виконав правильний route. Наприклад, слабка Jira оцінюється в Epic 08, а не через `PF-010`, якщо всі process obligations були пройдені.

Так само правильний документ не скасовує process failure: якщо модель вигадала critical fact, але випадково створила хороший Passport, `PF-003` застосовується.

## 7. RUN-sensitive interpretation

- `RUN_01`: основний акцент — clean route, no invention, correct completion.
- `RUN_02`: branch/obligation coverage; compound question не може приховати пропуск.
- `RUN_03`: завершення має бути `T_SCENARIO_EXHAUSTED`, а не штучний artifact package.
- `RUN_04`: corrections, invalidation, regeneration і approval versioning є blocking.
- `RUN_05`: `T_INPUT_BLOCKED` має бути чесним; вигадування missing input активує `PF-003`.

## 8. Registry governance

Зміна cap value або trigger є evaluation-contract change і вимагає:

- version bump registry;
- changelog;
- retroactive-score policy;
- explicit decision, чи переоцінюються historical attempts;
- synchronization із template/schema.

## 9. Machine-readable source

Канонічний machine-readable registry: `PROCESS_FAILURE_CAPS.yaml`.
