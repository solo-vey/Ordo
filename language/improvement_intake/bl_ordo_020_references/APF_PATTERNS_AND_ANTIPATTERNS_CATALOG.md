# Каталог патернів і антипатернів для History Event Analysis Package Factory

**Призначення:** вбудувати в головний пакет механізм виявлення типових помилок процесу, prompts, templates, gates та generated artifacts.

**База аналізу:** проблеми, виявлені під час тестування `history_event_analysis_package_factory_v0_8_8_prompt_registry_confirmed`, і виправлення, підтверджені в release `v0.8.10-confirmed-full-qa-automation`.

---

# 1. Як читати каталог

Кожен запис містить:

- **Антипатерн** — повторювана неправильна конструкція.
- **Симптоми** — як помилка проявляється в діалозі або артефактах.
- **Наш приклад** — реальний клас проблеми з поточного playbook.
- **Чому виникає** — root cause.
- **Наслідки** — що саме ламається.
- **Рекомендований патерн** — правильна модель.
- **Як ми вирішували** — застосоване виправлення.
- **Detection rule** — як пакет може автоматично або напівавтоматично знайти проблему.
- **Prevention gate** — де блокувати перехід або генерацію.

---

# 2. Архітектурні антипатерни процесу

## AP-01. Змішування design-time і runtime responsibilities

### Антипатерн

Один вузол одночасно:

- досліджує source row;
- проєктує event contract;
- визначає runtime mapping;
- припускає, що runtime має доступ до source row.

### Симптоми

У runtime mapping з’являються:

- `source_row.root_id`;
- `source_row.sub_type`;
- `source_row.date_modify`;
- інші поля, яких немає у фактичному runtime input.

### Наш приклад

HistoryEvent generator реально отримує тільки `ChangeRecord`, але ранні формулювання будували:

- `root_id` із source row;
- `item.isEdr` із `source_row.sub_type`;
- `item.date` із `source_row.date_modify`.

### Чому виникає

У вузлі змішані три responsibility:

1. evidence discovery;
2. contract design;
3. runtime execution mapping.

### Наслідки

- нереалізований контракт;
- прихована runtime dependency;
- implementation prompt не відповідає фактичному processor input;
- QA перевіряє не той execution path.

### Рекомендований патерн

**Design-time / Runtime Boundary Pattern**

- source row — design-time evidence;
- ChangeRecord — runtime input;
- static selected-path rules — окреме джерело;
- кожне поле має `source_kind`.

### Як ми вирішували

Зафіксували:

- `root_id ← ChangeRecord.data.root_id`;
- `source_change_id ← ChangeRecord._id`;
- `item.date ← ChangeRecord.date`;
- `item.year ← year(item.date)`;
- `item.isEdr ← selected tree path rule`;
- source row не є runtime dependency.

### Detection rule

Знайти у runtime mapping посилання на:

```text
source_row.*
source_document.*
original_record.*
```

і перевірити, чи ці об’єкти реально входять у runtime contract.

### Prevention gate

`RUNTIME_CHANGERECORD_ONLY_GATE`

---

## AP-02. God Node / змішування кількох process responsibilities в одному вузлі

### Антипатерн

Один вузол одночасно:

- визначає тестове покриття;
- збирає environment data;
- розподіляє manual/automated;
- проєктує runner flow;
- визначає execution mode;
- генерує manual runbook.

### Симптоми

- вузол має дуже великий prompt;
- частина результату регулярно пропускається;
- модель завершує вузол після першої секції;
- підтвердження вузла не означає завершеність усіх responsibility.

### Наш приклад

Початковий `B1_N5` намагався охопити весь QA, але фактично модель видавала лише functional tests і переходила далі.

### Чому виникає

Немає separation of concerns на process-рівні.

### Наслідки

- partial node completion;
- незібрані operational data;
- automation plan змішується з runner spec;
- manual package генерується з неповного стану.

### Рекомендований патерн

**Single Responsibility Node Pattern**

Розділення:

- `B1_N5` — coverage model;
- `B1_N5A` — QA environment intake;
- `B1_N5C` — execution allocation;
- `B1_N5D` — automation execution design;
- `B1_N5E` — execution mode;
- `B1_N5B` — manual runbook design;
- `B1_P5` — artifact generation.

### Як ми вирішували

Створили окремі вузли й transitions між ними.

### Detection rule

Вузол має більше ніж один із класів виходу:

```text
coverage
environment
allocation
execution_design
execution_mode
runbook
artifact_generation
```

### Prevention gate

`NODE_SINGLE_RESPONSIBILITY_GATE` — рекомендований новий meta-gate.

---

## AP-03. Partial Node Completion

### Антипатерн

Модель показує одну частину обов’язкового output і вважає вузол завершеним.

### Симптоми

- є functional tests, але немає unit/integration;
- є test list, але немає automation explanation;
- модель просить підтвердження або переходить далі до заповнення всіх required sections.

### Наш приклад

`B1_N5` видав functional tests, але unit tests з’явилися тільки після окремого запитання користувача.

### Чому виникає

Required output описаний як prose, але не має completion marker.

### Наслідки

- downstream artifacts неповні;
- користувач не знає, що частина вузла пропущена;
- generated Passport/Jira не мають повного coverage.

### Рекомендований патерн

**Atomic Completion Contract**

Кожен вузол має:

- `required_sections`;
- `completion_marker`;
- заборону `confirm/next`, доки всі секції не показані.

### Як ми вирішували

Додали hard completion rules до `B1_N5` та prompt `hp.qa.after_contract.v1`.

### Detection rule

Порівняти `required_sections` вузла з фактично видимими секціями response.

### Prevention gate

`B1_N5_FULL_QA_NODE_COMPLETION_GATE`

---

## AP-04. Hidden State / невидиме відновлення контракту

### Антипатерн

Модель використовує реконструйовані або попередньо підтверджені значення, але не показує їх користувачу.

### Симптоми

- наступний вузол працює з delta contract, якого не було у видимій відповіді;
- користувач не бачить, що old/new/date були reconstructed;
- підтверджується стан, який не був явно показаний.

### Наш приклад

Коли ChangeRecord ще не надано, мінімальний delta contract міг бути reconstructed із source evidence, але раніше це відбувалося неявно.

### Рекомендований патерн

**Visible State Reconstruction Pattern**

Перед переходом показати:

- reconstruction mode;
- statuses;
- source row path;
- `delta.field`;
- old/new/date/source_change_id;
- open gaps;
- пояснення, що source row не доводить факт change.

### Як ми вирішували

Посилили `B1_N2B` і prompts:

- `hp.delta_intake.status_prefilter.v1`;
- `hp.delta_intake.single_field.v1`.

### Detection rule

Якщо downstream state заповнений не з direct user input, має існувати visible reconstruction block.

### Prevention gate

`VISIBLE_RECONSTRUCTED_STATE_GATE` — рекомендований meta-gate.

---

## AP-05. State Loss між вузлами

### Антипатерн

Підтверджене раніше правило повторно інтерпретується або втрачається.

### Симптоми

- confirmed fallback знову ставиться під сумнів;
- наступний вузол використовує default замість confirmed value;
- різні artifacts отримують різні значення.

### Наш приклад

Stored-value fallback `"-"` був уже підтверджений, але міг повторно трактуватися як rendering fallback.

### Рекомендований патерн

**Confirmed State Is Immutable Until Explicitly Reopened**

- human-confirmed state має вищий пріоритет за templates/examples;
- наступний вузол читає його як confirmed pending input;
- змінити можна лише через explicit reopening.

### Як ми вирішували

Додали правило у `B1_P1` і source-priority chain.

### Detection rule

Порівняти нове значення поля з confirmed state. Будь-яка різниця без `reopened_by_human=true` — помилка.

### Prevention gate

`CONFIRMED_STATE_PRESERVATION_GATE`

---

# 3. Семантичні антипатерни event contract

## AP-06. Operation Type Inference from Delta Presence

### Антипатерн

Операцію над записом визначають за наявністю `delta.old` або `delta.new`.

### Помилкова логіка

- old missing + new present → record added;
- old present + new missing → record deleted.

### Наш приклад

Для email change така інтерпретація була запропонована під час проєктування trigger/no-op.

### Чому це неправильно

`delta.old/new` описують зміну значення поля, а не тип операції над record.

Операція визначається тільки:

`ChangeRecord.data.item.status`

### Рекомендований патерн

**Status-First Operation Semantics**

Порядок:

1. status;
2. delta.field;
3. normalization;
4. readiness;
5. dedup;
6. create.

### Як ми вирішували

Зафіксували:

- old missing + new present → field changed absent → present;
- old present + new missing → field changed present → absent;
- both missing → no change;
- `new/modified/deleted` — тільки status.

### Detection rule

Знайти правила, де operation alias залежить від:

```text
old is null
new is null
old exists
new exists
```

### Prevention gate

Частина `B1_N4` і `CROSS_DOCUMENT_CONTRACT_CONSISTENCY_GATE`.

---

## AP-07. Conflating Comparison Value and Stored Value

### Антипатерн

Одне й те саме fallback-значення використовується:

- для normalization/comparison;
- для payload storage;
- для rendering.

### Наш приклад

`"-"` спочатку трактувався як UI-only fallback або міг потрапити у comparison.

### Правильний контракт

- comparison empty → `""`;
- stored empty → ASCII `"-"`;
- rendering не виконує fallback.

### Рекомендований патерн

**Three-Layer Value Semantics**

1. raw value;
2. normalized comparison value;
3. stored payload value.

### Як ми вирішували

Оновили `COMMON_N4A` і prompt `hp.normalization.stored_values_fallback.v1`.

### Detection rule

Перевірити, чи один placeholder використовується і в predicate, і в payload.

### Prevention gate

`STORED_VALUES_FALLBACK_GATE`

---

## AP-08. Rendering Layer Owns Business Fallback

### Антипатерн

Template або UI підмінює null/empty на placeholder.

### Симптоми

- payload містить null/empty;
- різні clients показують різні значення;
- automation assertion не знає, що перевіряти;
- fallback не зберігається в HistoryEvent.

### Рекомендований патерн

**Persisted Presentation Value Pattern**

Fallback формується під час створення `item.values`, а template лише підставляє вже збережене значення.

### Як ми вирішували

Заборонили template/render fallback.

### Detection rule

Пошук у templates:

```text
default("-")
coalesce(value, "-")
value || "-"
```

коли контракт вимагає persisted fallback.

### Prevention gate

`STORED_VALUES_FALLBACK_GATE`

---

## AP-09. Silent Date Fallback Chain

### Антипатерн

Якщо основна дата відсутня, модель мовчки пробує:

- `date_create`;
- `changed_at`;
- `date_change`;
- `source_row.date_modify`.

### Наслідки

- event chronology стає непередбачуваною;
- artifacts описують різні date sources;
- тест може пройти з неправильною датою.

### Рекомендований патерн

**Single Authoritative Date Source**

- `item.date ← ChangeRecord.date`;
- `item.year ← year(date)`;
- missing/invalid → blocked;
- fallback — тільки explicitly confirmed та runtime-available.

### Як ми вирішували

Посилили `COMMON_N4A`, `B1_N2C`, runtime mapping contract.

### Detection rule

У mapping має бути один authoritative date source або explicit fallback object із proof of runtime availability.

### Prevention gate

`RUNTIME_CHANGERECORD_ONLY_GATE`

---

## AP-10. Source Evidence Becomes Runtime Dependency

### Антипатерн

Поле, знайдене в source row для аналізу, автоматично використовується в generator mapping.

### Відмінність від AP-01

AP-01 — архітектурне змішування responsibility.  
AP-10 — конкретний механізм помилки: evidence promotion without runtime proof.

### Рекомендований патерн

**Evidence-to-Mapping Proof Rule**

Кожне mapping field має:

- `evidence_source`;
- `runtime_source`;
- `mapping_type`;
- `proof_of_availability`.

### Detection rule

Якщо `evidence_source != runtime_source`, але немає explicit translation rule — block.

---

## AP-11. Missing Value Treated as Missing Contract

### Антипатерн

Відсутній `delta.old` або `delta.new` автоматично вважається incomplete input.

### Наш приклад

Для email:

- old missing + new present — валідна зміна;
- old present + new missing — валідна зміна.

### Рекомендований патерн

**Nullable Delta Input Pattern**

`old/new` — nullable/missing comparison inputs, не mandatory contract fields.

Block only if відсутні:

- `_id`;
- `data.root_id`;
- valid `date`;
- required static mapping.

### Detection rule

Якщо readiness condition вимагає одночасну наявність old і new — flag.

---

## AP-12. Placeholder Character Drift

### Антипатерн

Різні артефакти використовують:

- `-` ASCII hyphen-minus;
- `—` em dash;
- порожній рядок;
- `null`.

### Наш приклад

Passport, implementation prompt і manual QA могли містити різні символи.

### Рекомендований патерн

**Exact Scalar Contract**

Placeholder є exact byte-level contract, а не “візуально схожий символ”.

### Detection rule

Порівняти Unicode code points placeholder у всіх artifacts.

### Prevention gate

`CROSS_DOCUMENT_CONTRACT_CONSISTENCY_GATE`

---

## AP-13. Placeholder Key Drift

### Антипатерн

Одне й те саме значення називається:

- `old_value`;
- `oldEmail`;
- `old#email`;
- `prev#email`.

### Рекомендований патерн

**Canonical Placeholder Key Pattern**

- `old#<last_attribute>`;
- `new#<last_attribute>`.

Для email:

- `old#email`;
- `new#email`.

### Detection rule

Усі template placeholders мають бути subset canonical `item.values` keys.

### Prevention gate

`B1_N4B` + cross-document gate.

---

# 4. Prompt і registry антипатерни

## AP-14. Prompt Bound to Node Identity

### Антипатерн

Prompt ID містить node ID або prompt існує тільки як inline-text вузла.

### Наслідки

- складно reuse;
- зміна дерева ламає references;
- немає stable prompt registry;
- важко підтверджувати prompt незалежно від node.

### Рекомендований патерн

**Stable Semantic Prompt IDs**

Наприклад:

`hp.normalization.stored_values_fallback.v1`

а не:

`B1_N4A_PROMPT_3`.

### Як ми вирішували

Використали `prompts/registry.yaml` і `guidance_refs`.

### Detection rule

Prompt ID не повинен залежати від current node path, якщо prompt семантично reusable.

### Prevention gate

Prompt registry referential integrity check.

---

## AP-15. Inline Prompt Duplication

### Антипатерн

Одна інструкція копіюється у кілька вузлів і templates.

### Симптоми

- одна версія оновлена, інші — ні;
- однакове правило сформульоване по-різному;
- cross-document drift.

### Рекомендований патерн

**Single Prompt Source + References**

- prompt file;
- stable ID;
- node `guidance_refs`;
- templates не дублюють semantics без потреби.

### Detection rule

Semantic duplicate detection або exact duplicated blocks.

---

## AP-16. Prompt Describes Output, but Not Completion

### Антипатерн

Prompt каже “додай unit tests”, але не каже:

- скільки секцій;
- які поля обов’язкові;
- коли вузол завершений;
- що не можна переходити далі.

### Рекомендований патерн

**Prompt Completion Contract**

Кожен prompt має:

- required output sections;
- forbidden omissions;
- completion condition;
- next-node prohibition on incomplete result.

### Наш приклад

`hp.qa.after_contract.v1` був посилений саме так.

---

## AP-17. Example Becomes Authority

### Антипатерн

Приклад документа або fixture сприймається як повний підтверджений склад.

### Наш приклад

Приклад manual QA із п’ятьма TC був сприйнятий як список усіх manual tests, хоча він показував лише формат.

### Наслідки

- confirmed test set скорочується;
- generated artifact відображає example, а не allocation state.

### Рекомендований патерн

**Examples Are Non-Authoritative by Default**

Пріоритет:

1. human-confirmed state;
2. confirmed prompts;
3. authoritative specs;
4. templates;
5. examples.

### Detection rule

Якщо generated IDs дорівнюють example IDs, але не confirmed allocation IDs — fail.

### Prevention gate

`GENERATED_DOCUMENT_TEST_COVERAGE_GATE`

---

# 5. Template та artifact-generation антипатерни

## AP-18. Template Exists but Is Not Bound to Generation Step

### Антипатерн

У пакеті є правильний template, але generation node не зобов’язаний його використовувати.

### Наш приклад

`MANUAL_FUNCTIONAL_TESTS_TEMPLATE.md` існував, але `05_QA_PACKAGE` генерувався в іншому форматі.

### Рекомендований патерн

**Explicit Template Binding**

У generation node для кожного artifact:

- artifact name;
- authoritative template;
- authoritative source state;
- post-generation gate.

### Як ми вирішували

Посилили `B1_P5`.

### Detection rule

Кожен required artifact має рівно один active authoritative template binding.

---

## AP-19. Artifact Existence Check Instead of Content Check

### Антипатерн

Gate перевіряє лише, що файл існує.

### Симптоми

- Passport є, але test tables відсутні;
- Jira є, але functional scenarios не включені;
- manual package є, але немає rollback;
- runner YAML є, але це coverage matrix.

### Рекомендований патерн

**Semantic Artifact Gate**

Перевіряти:

- required sections;
- expected IDs;
- counts;
- field contracts;
- allocation;
- content type.

### Як ми вирішували

Додали:

- `GENERATED_DOCUMENT_TEST_COVERAGE_GATE`;
- `MANUAL_QA_PACKAGE_COMPLETENESS_GATE`;
- `QA_AUTOMATION_RUNNER_SPEC_SCHEMA_GATE`.

---

## AP-20. Multiple Artifact Types in One File

### Антипатерн

Один файл одночасно є:

- allocation matrix;
- automation plan;
- executable runner spec;
- execution report.

### Наш приклад

`08_QA_AUTOMATION_SPEC` спочатку був coverage/target plan, хоча назва очікувала runnable spec.

### Рекомендований патерн

**Artifact Type Purity**

Окремо:

- allocation state;
- execution design;
- runner spec;
- run report.

### Detection rule

Artifact має declared `kind` і schema, що відповідає тільки одному типу.

### Prevention gate

`QA_AUTOMATION_RUNNER_SPEC_SCHEMA_GATE`

---

## AP-21. Generated Document Omits Confirmed Test Catalog

### Антипатерн

Artifacts генеруються з prose summary, а не зі structured test model.

### Наш приклад

Passport/Jira не містили всіх FUNC-TC/UNIT-TC.

### Рекомендований патерн

**Structured Test Catalog as Single Source**

- `FUNC-TC-*`;
- `UNIT-TC-*`;
- allocation metadata;
- artifact-specific rendering rules.

### Розподіл

- Passport: all FUNC + all UNIT;
- Jira: all FUNC, no UNIT;
- Manual QA: exactly `manual_qa_ids`;
- Automation spec: exactly `automated_ids`.

### Detection rule

Set equality між confirmed IDs та artifact IDs.

---

## AP-22. Placeholder-Only Required Artifact

### Антипатерн

Required file генерується з TODO/placeholder замість executable content.

### Наслідки

- package формально complete;
- practically unusable;
- readiness overstated.

### Рекомендований патерн

**Honest Readiness Classification**

- `draft`;
- `executable`;
- `blocked`;
- `automation-ready`;
- `executed_with_report`.

Placeholder допускається тільки у draft і має бути listed as open gap.

---

# 6. QA-антипатерни

## AP-23. Functional-Only QA Presented as Full QA

### Антипатерн

Functional scenarios називаються повним QA coverage.

### Наш приклад

Unit/provider tests та integration tests з’явилися лише після уточнення.

### Рекомендований патерн

**Layered QA Coverage**

Окремі каталоги:

- functional;
- unit/provider;
- integration;
- automation explanation;
- manual/reviewer notes;
- open gaps.

### Prevention gate

`B1_N5_FULL_QA_NODE_COMPLETION_GATE`

---

## AP-24. Mixing Test Coverage and Test Execution Allocation

### Антипатерн

Факт існування test case автоматично означає, що він має бути:

- manual;
- automated;
- у певному рівні.

### Рекомендований патерн

**Coverage First, Allocation Second**

1. сформувати повний test catalog;
2. для кожного FUNC-TC визначити:
   - Manual QA yes/no;
   - Automated yes/no;
   - levels;
   - exclusion reason.

### Як ми вирішували

Створили `B1_N5C`.

---

## AP-25. Strategy Chosen Before Allocation

### Антипатерн

Automation strategy визначається до рішення, чи test взагалі автоматизується.

### Рекомендований патерн

**Allocation Before Execution Design**

- `B1_N5C` — what is automated;
- `B1_N5D` — how each automated test runs.

---

## AP-26. Unit Coverage Replaces Functional Test Identity

### Антипатерн

Functional scenario, покритий на unit level, перестає вважатися FUNC-TC або перейменовується в UNIT-TC.

### Рекомендований патерн

**Orthogonal Test Identity and Execution Level**

- FUNC-TC описує business behavior;
- UNIT-TC описує component behavior;
- automation levels не змінюють identity.

### Detection rule

`functional_tc_id` не може бути замінений `unit_tc_id` через level allocation.

---

## AP-27. Manual Runbook Generated Without Operational Data

### Антипатерн

Manual test описує business expectation, але не має:

- database/collection;
- endpoint;
- fixture;
- lookup;
- projection;
- rollback;
- security constraints.

### Наш приклад

Перший manual package був концептуальним, а не executable.

### Рекомендований патерн

**Environment Intake Before Runbook**

Спочатку `B1_N5A`, потім `B1_N5B`.

### Prevention gate

`MANUAL_QA_PACKAGE_COMPLETENESS_GATE`

---

## AP-28. Unsafe or Unbounded QA Lookup

### Антипатерн

QA інструкція читає весь документ або не використовує projection/stable identifiers.

### Наслідки

- витік даних;
- нестабільні fixtures;
- надмірний output;
- складний rollback.

### Рекомендований патерн

**Minimal Projection + Stable Lookup**

Кожен lookup має:

- stable selector;
- projection;
- очікуваний cardinality;
- safe logging rule.

---

## AP-29. Mutation Without Rollback

### Антипатерн

Manual або automated test змінює source state, але не відновлює його.

### Рекомендований патерн

**Reversible Test Flow**

- baseline capture;
- mutation;
- assertions;
- rollback;
- post-rollback verification.

### Prevention gate

Manual completeness та runner schema gates.

---

# 7. Automation runner антипатерни

## AP-30. Coverage Matrix Masquerading as Runner Spec

### Антипатерн

YAML містить список test IDs і target levels, але не містить executable steps.

### Наш приклад

Один із generated `08_QA_AUTOMATION_SPEC` був automation plan, не runner-compatible spec.

### Рекомендований патерн

**Executable Runner Contract**

Для кожного AUTO-TC:

- strategy;
- setup/input;
- action;
- ChangeRecord handling;
- processing;
- expected events/absence/errors;
- polling;
- rollback/cleanup.

---

## AP-31. One Strategy Forced on All Tests

### Антипатерн

Усі tests примусово реалізуються як REST + Mongo source patch.

### Чому неправильно

Різні тести потребують:

- `source_patch_flow`;
- `synthetic_change_record`;
- `provider_unit_fixture`;
- `integration_fixture`;
- `concurrency_flow`.

### Рекомендований патерн

**Strategy by Test Nature**

### Detection rule

Якщо всі AUTO-TC мають одну strategy без semantic justification — warning.

---

## AP-32. Execute Used as Runner Status

### Антипатерн

`suite.status = execute`.

### Правильна модель

Runner statuses:

- `draft`;
- `automation-ready`.

Process modes:

- `draft`;
- `automation-ready`;
- `execute`.

У mode `execute` YAML status лишається `automation-ready`, після чого suite запускається.

### Prevention gate

`QA_AUTOMATION_RUNNER_SPEC_SCHEMA_GATE`

---

## AP-33. Schema Pass Equals Test Pass

### Антипатерн

Успішний YAML parse/schema validation називається успішним виконанням tests.

### Наш приклад

Runner знаходив 6 tests, але skip-ав їх через status. Це не execution success.

### Рекомендований патерн

**Separated Execution Evidence**

Окремо:

- YAML parsing;
- schema compatibility;
- discovered;
- executed;
- skipped;
- passed/failed assertions;
- rollback.

---

## AP-34. Skipped Equals Passed

### Антипатерн

Discovered або skipped test додається до passed count.

### Рекомендований патерн

Строге правило:

```text
skipped != executed
skipped != passed
discovered != executed
```

### Prevention gate

`AUTOMATION_RUN_REPORT_GATE`

---

## AP-35. Business Failure Classified as Runner Failure

### Антипатерн

Assertion mismatch трактують як schema/runner incompatibility та регенерують YAML.

### Наш приклад

5 tests passed, 1 business assertion failed, rollback 6/6 passed.

### Рекомендований патерн

**Failure Domain Separation**

- schema failure;
- runner contract failure;
- environment blocker;
- business assertion failure;
- rollback failure.

Business failure зберігає execution evidence і повертається на implementation/expectation analysis.

---

## AP-36. No-Event Flow Requires Fake Change ID

### Антипатерн

Для no-op scenario runner вигадує `CHANGE_ID`, щоб пройти загальний flow.

### Рекомендований патерн

**Branch-Aware Runner Flow**

- якщо ChangeRecord не створено — не викликати processing, що потребує ID;
- перевірити expected absence;
- не використовувати fake ID.

---

## AP-37. Async Flow Without Polling Contract

### Антипатерн

Runner відразу читає HistoryEvent після action.

### Рекомендований патерн

**Explicit Polling Contract**

- timeout;
- interval;
- stop condition;
- timeout classification.

---

# 8. Gate та readiness антипатерни

## AP-38. Gate Checks Syntax but Not Semantics

### Антипатерн

Gate перевіряє YAML parse або required root keys, але не перевіряє IDs, mappings, expected outcomes.

### Рекомендований патерн

**Layered Gate Model**

1. syntax;
2. schema;
3. semantic completeness;
4. cross-artifact consistency;
5. readiness.

---

## AP-39. Generation Success Equals Package Readiness

### Антипатерн

Файли згенеровані — значить package ready.

### Рекомендований патерн

**Generation / Validation / Readiness Separation**

- generated;
- structurally valid;
- semantically consistent;
- draft-ready;
- automation-ready;
- executed-with-report.

---

## AP-40. Packaging Without Explicit Human Command

### Антипатерн

Модель автоматично створює final zip після gate pass.

### Рекомендований патерн

**Explicit Release Commit**

Final zip тільки після команди:

`збери`

### Як ми вирішували

Закріпили у `FINAL_PACKAGE_READINESS_GATE`.

---

## AP-41. Failed Business Suite Hidden by Correct Report

### Антипатерн

Report structurally valid, тому package називається “passed”.

### Рекомендований патерн

Розділяти:

- `report_gate_status`;
- `suite_business_status`.

Можлива чесна комбінація:

```text
report_gate_status: passed
suite_business_status: partially_failed
```

---

## AP-42. Cross-Document Drift

### Антипатерн

Passport, Jira, implementation prompt, manual QA та automation YAML описують різні contracts.

### Типові розходження

- різний alias;
- різні statuses;
- `"-"` vs `"—"`;
- різні placeholder keys;
- різні date mappings;
- різні test IDs;
- manual/automated allocation drift.

### Рекомендований патерн

**Single Confirmed Contract + Cross-Document Gate**

### Prevention gate

`CROSS_DOCUMENT_CONTRACT_CONSISTENCY_GATE`

---

## AP-43. Manifest as Inventory Only

### Антипатерн

Manifest містить лише список файлів.

### Рекомендований патерн

**Traceability Manifest**

Manifest має містити:

- package version;
- baseline;
- lineage;
- changed nodes/prompts/gates;
- artifact paths;
- template/spec bindings;
- rendered test IDs;
- validation statuses;
- open gaps;
- checksums.

---

## AP-44. Version Label Drift

### Антипатерн

У новому release залишаються startup/docs із старою version label, і наступний чат сприймає її як authoritative.

### Рекомендований патерн

**Single Authoritative Version Source**

Версія визначається manifest/package metadata; stale labels мають бути lint error або explicit known issue.

---

# 9. Human interaction антипатерни

## AP-45. Batch Confirmation Without Request

### Антипатерн

Модель показує багато змінених вузлів і просить підтвердити все одним “так”.

### Рекомендований патерн

**One Node at a Time Confirmation**

Для кожного вузла:

- повний node contract;
- повний текст attached prompts;
- одне підтвердження;
- потім наступний вузол.

---

## AP-46. Prompt IDs Shown Without Prompt Text

### Антипатерн

Під час confirmation модель показує лише:

`guidance_refs: [...]`

але не показує, що саме буде виконувати prompt.

### Рекомендований патерн

**Inspectable Guidance Confirmation**

Показувати full prompt text для кожного attached prompt.

---

## AP-47. Ordinary Conversation Instead of Process Driving

### Антипатерн

Після переносу в новий чат модель просто відповідає на тему, але не відновлює:

- operating mode;
- checkpoint;
- current node;
- formal transitions;
- candidate state.

### Рекомендований патерн

**Process Bootstrap + Checkpoint Resume**

Новий чат має прочитати:

- start file;
- checkpoint;
- executable model;
- prompt registry;
- process driver protocol.

---

## AP-48. Wrong Process Resume Point

### Антипатерн

Після завершеного release новий чат автоматично стартує `ROOT_N0`.

### Правильний стан після v0.8.10

```text
operating_mode = factory_maintenance_continuation
checkpoint = RELEASE_V0_8_10_BUILT_AND_CONFIRMED
current_node = null
```

`ROOT_N0` запускається лише після explicit команди:

`запусти factory для нової події`

---

# 10. Рекомендована системна модель patterns/antipatterns у головному пакеті

## 10.1. Запропонована структура

```text
patterns/
  registry.yaml
  process/
  runtime/
  qa/
  automation/
  generation/
  release/

antipatterns/
  registry.yaml
  process/
  runtime/
  qa/
  automation/
  generation/
  release/

gates/
  meta/
    NODE_SINGLE_RESPONSIBILITY_GATE.yaml
    CONFIRMED_STATE_PRESERVATION_GATE.yaml
    ARTIFACT_TYPE_PURITY_GATE.yaml
    EXAMPLE_NON_AUTHORITY_GATE.yaml
```

## 10.2. Мінімальна schema запису

```yaml
id: AP-XX
name: human-readable name
category: process|runtime|qa|automation|generation|release
severity: warning|blocking
description: ...
signals:
  - ...
bad_example:
  - ...
correct_pattern:
  id: P-XX
  description: ...
detection:
  mode: static|runtime|human_review|cross_artifact
  rules:
    - ...
prevention:
  node_ids:
    - ...
  prompt_ids:
    - ...
  gate_ids:
    - ...
remediation:
  - ...
evidence:
  baseline: history_event_analysis_package_factory_v0_8_8_prompt_registry_confirmed
  resolved_in: v0.8.10-confirmed-full-qa-automation
```

## 10.3. Severity policy

### Blocking

Антипатерн блокує next/generation/release, якщо може:

- створити нереалізований runtime contract;
- втратити confirmed state;
- змінити business semantics;
- пропустити confirmed tests;
- створити unsafe QA flow;
- назвати skipped tests passed;
- приховати business failure;
- створити inconsistent package.

### Warning

Антипатерн дає warning, якщо:

- не ламає correctness прямо зараз;
- створює maintenance risk;
- дублює semantics;
- погіршує traceability;
- містить stale naming/version labels.

---

# 11. Рекомендований порядок інтеграції

## Етап 1. Registry

Створити:

- `patterns/registry.yaml`;
- `antipatterns/registry.yaml`.

Внести AP-01 — AP-48.

## Етап 2. Node-level detection

Кожен вузол отримує:

```yaml
applicable_antipattern_checks:
  - AP-...
expected_patterns:
  - P-...
```

## Етап 3. Generation-time gates

Перед `B1_P5`:

- responsibility checks;
- state preservation;
- artifact type purity;
- template binding;
- test allocation completeness.

## Етап 4. Post-generation checks

Після generation:

- semantic artifact gates;
- cross-document consistency;
- runner schema;
- report classification;
- release readiness.

## Етап 5. Feedback loop

Кожен новий production/test finding класифікується:

```text
existing antipattern
new variant
new antipattern
implementation defect outside factory
```

Якщо новий антипатерн підтверджено:

1. додати registry entry;
2. прив’язати affected nodes/prompts/templates;
3. додати detection rule;
4. додати або посилити gate;
5. додати regression test;
6. зафіксувати resolved version.

---

# 12. Коротка матриця «антипатерн → наше виправлення»

| Антипатерн | Виправлення |
|---|---|
| Design-time змішано з runtime | ChangeRecord-only runtime mapping |
| God QA node | B1_N5A–B1_N5E + B1_N5B |
| Partial node completion | required sections + hard completion gate |
| Hidden reconstructed state | visible delta contract |
| Confirmed state loss | confirmed-state priority |
| Operation from old/new | status-first semantics |
| Compare/store fallback mixed | `""` for compare, `"-"` for storage |
| Rendering fallback | persisted fallback |
| Silent date fallbacks | ChangeRecord.date only |
| Missing old/new = incomplete | nullable delta inputs |
| Prompt tied to node | stable semantic prompt IDs |
| Example treated as authority | source priority chain |
| Template exists but unused | explicit template binding |
| File exists = complete | semantic content gates |
| Coverage plan = runner spec | artifact type purity |
| Functional-only = full QA | layered QA coverage |
| Coverage = allocation | separate B1_N5C |
| One strategy for all tests | strategy by test nature |
| Manual tests without environment | B1_N5A before B1_N5B |
| Mutation without rollback | reversible test flow |
| Execute as status | separate mode and status |
| Schema pass = tests pass | separated execution evidence |
| Skipped = passed | strict count semantics |
| Business failure = runner failure | failure domain separation |
| Async without polling | explicit polling contract |
| Generation = readiness | final readiness model |
| Auto packaging | explicit `збери` |
| Cross-document drift | cross-document gate |
| Chat reset loses process | bootstrap + checkpoint resume |

---

# 13. Рекомендація для головного пакета

Цей каталог варто використати не як документацію “для читання”, а як executable meta-layer.

Мінімальний механізм:

1. перед кожним next transition перевірити node-level antipatterns;
2. перед artifact generation перевірити process/generation antipatterns;
3. після generation перевірити semantic artifact antipatterns;
4. перед release перевірити readiness/release antipatterns;
5. кожен failure повинен показати:
   - antipattern ID;
   - знайдений signal;
   - affected component;
   - recommended return node;
   - remediation;
   - чи потрібне human confirmation.

Рекомендований формат visible failure:

```yaml
antipattern_id: AP-20
name: Multiple Artifact Types in One File
detected_in: 08_QA_AUTOMATION_SPEC_<ALIAS>.yaml
signal: test_cases replaced by allocation matrix
severity: blocking
return_to: B1_N5D
remediation: regenerate executable runner specification
```

---

# 14. Статус цього документа

Документ є design proposal для інтеграції в головний APF package.

Він не змінює автоматично release `v0.8.10`. Для фактичного внесення в package рекомендовано окремо:

- додати registry files;
- створити meta-gates;
- прив’язати checks до nodes;
- додати regression tests;
- пройти покрокове підтвердження;
- зібрати нову версію тільки після команди `збери`.
