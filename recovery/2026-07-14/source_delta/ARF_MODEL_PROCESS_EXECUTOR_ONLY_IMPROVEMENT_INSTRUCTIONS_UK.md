# Інструкції для моделі, яка формує ARF: жорстка керованість робочих playbook

## Мета

ARF має створювати playbook як детермінований виконуваний контракт, а не як рекомендаційний текст для творчої моделі.

## 1. Default control model

Кожен робочий playbook повинен за замовчуванням оголошувати:

- `runtime_mode: PROCESS_EXECUTOR_ONLY`;
- `decision_model: closed_world`;
- `default_role: executor`;
- `undefined_action: blocked_missing_instruction`.

Модель не є автором, редактором, дизайнером або оптимізатором процесу.

## 2. Allowlist для кожного вузла

ARF повинен вимагати для кожного node:

- одну atomic responsibility;
- точні prerequisites;
- точні дозволені inputs;
- точні дозволені actions;
- required outputs;
- validation gates;
- explicit transitions;
- forbidden transitions;
- invalidation effects;
- authorization boundary.

Дія, якої немає в allowlist вузла, заборонена.

## 3. Розділення режимів

ARF повинен генерувати три взаємовиключні режими:

1. `EXECUTION_MODE` — суворе виконання active node без творчих змін.
2. `DESIGN_MODE` — лише пропозиції змін; package/repository mutation заборонена.
3. `AUTHORIZED_MAINTENANCE_MODE` — зміни playbook/factory лише після explicit user authorization і тільки в погодженому scope.

Не допускається неявний перехід між режимами.

## 4. Instruction hierarchy

ARF повинен закріпити незмінний порядок:

`confirmed user decision → active node contract → authoritative prompt → canonical template → confirmed state → artifact validator → rendered artifact → independent validation result`.

Нижчий рівень не може перевизначати вищий.

## 5. Заборона editorial freedom

У generated contracts додавати hard prohibitions на:

- скорочення, об’єднання, перестановку або пропуск mandatory nodes;
- заміну повторюваних required blocks shared/common section;
- `same as above`, `see common steps`, cross-reference замість executable content;
- вигадування template variants, data, permissions, evidence або completion state;
- трактування одного confirmation як іншого authorization;
- самостійне “покращення” структури документа.

## 6. Незалежна validation

Artifact не може сам оголосити `passed`. ARF має створювати окремі validator nodes із machine-checkable outputs.

Для складених артефактів validation виконується на найменшій executable unit, а не лише на документі загалом.

## 7. Manual QA specialization

Для кожного test case ARF повинен вимагати локально присутні:

- ID і мету;
- передумови;
- точні test data;
- authorization requirement;
- впорядковані concrete steps;
- positive і negative assertions;
- evidence requirements;
- rollback steps;
- post-rollback assertions;
- result status.

Validator повинен ізолювати один TC, видалити всі shared sections та інші TC й перевірити, що сценарій залишається виконуваним.

## 8. Ambiguity handling

Коли даних або інструкцій бракує, ARF повинен генерувати blocking state:

```yaml
status: blocked_missing_instruction
allowed_action: request_exact_user_decision
```

Не створювати fallback на “best judgement”.

## 9. Anti-pattern generation

Під час створення playbook ARF має автоматично сформувати anti-pattern checks щонайменше для:

- node skipping;
- aggregate confirmation leakage;
- authorization scope leakage;
- editorial compression;
- shared-step substitution;
- invented source/template;
- document-level validation masking unit-level defects;
- self-declared validation;
- stale downstream confirmation;
- premature completion.

## 10. Acceptance criteria для ARF output

ARF output приймається лише якщо:

- усі executable nodes мають allowlists і forbidden actions;
- немає implicit transitions;
- кожна ambiguity має blocking route;
- modes мають explicit entry conditions;
- validators незалежні від artifacts;
- composite artifacts перевіряються на atomic-unit level;
- regression suite містить негативні сценарії редакторської або творчої самодіяльності моделі.
