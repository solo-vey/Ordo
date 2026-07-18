# ORDO — Правила формування типів playbook із YAML-джерела

Версія: 1.0  
Статус: нормативний transfer-документ для включення у процес створення benchmark playbook

## 1. Призначення

Цей документ визначає, як із одного авторитетного YAML playbook формувати різні представлення процесу для benchmark-порівняння.

Усі представлення повинні:

- реалізовувати той самий бізнес-процес;
- працювати з тими самими тестовими сценаріями;
- використовувати однакові авторитетні факти, класи, атрибути, шаблони та contracts;
- зберігати fail-closed, correction, invalidation, revalidation, reapproval і terminal semantics;
- відрізнятися способом подання процесу, а не змістом бізнес-логіки;
- мати окремі compilation rules і representation-specific validators.

YAML залишається source of truth для процесу, якщо для конкретного benchmark не зафіксовано інше.

---

## 2. Спільні інваріанти для всіх YAML-derived представлень

Незалежно від формату, не можна втрачати або послаблювати:

1. preflight та правила hard stop;
2. mandatory facts і заборону їх вигадування;
3. розрізнення `confirmed`, `proposed`, `fixture-only`, `unavailable`, `withdrawn`, `superseded`;
4. route isolation між RUN;
5. правила no-op і duplicate;
6. correction ownership;
7. invalidation залежних артефактів;
8. regeneration → revalidation → reapproval;
9. validator failure як блокуючий факт;
10. заборону self-authored PASS receipts;
11. approval binding до current artifact version/hash;
12. cross-artifact consistency;
13. route-specific output restrictions;
14. terminal evidence;
15. заборону self-scoring, якщо вона задана джерелом.

Кожен варіант має бути семантично зіставлений з YAML на рівні:

- intent;
- inputs;
- outputs;
- state mutation;
- evidence;
- success/failure conditions;
- transitions;
- correction owner;
- terminal outcome.

---

# 3. YAML Playbook

## 3.1. Призначення

Максимально формалізоване машинне представлення процесу.

## 3.2. Вимоги

YAML може і повинен містити:

- nodes/steps;
- stable IDs;
- node types;
- transitions;
- gates;
- state mutations;
- required inputs;
- produced outputs;
- schemas;
- validators;
- contracts;
- evidence requirements;
- terminal routes;
- correction and invalidation rules;
- machine-readable fixture bindings.

## 3.3. Стиль

- технічний;
- детермінований;
- однозначний;
- придатний для автоматичної валідації;
- без навмисної історичної нерівномірності.

## 3.4. Заборонено

- ховати критичну логіку лише у prose notes;
- мати неоднозначні transitions;
- залишати критичні поля без schema/contract;
- змішувати evaluator-only дані з model-visible runtime input.

## 3.5. Обов’язкові перевірки

- schema validation;
- graph closure;
- reachability;
- terminal-path validation;
- duplicate ID detection;
- state mutation consistency;
- correction-loop reachability;
- source-lock integrity;
- positive і negative fixtures.

---

# 4. Structured Instructions

## 4.1. Призначення

Структурований, послідовний і читабельний процес для аналітика, але без машинного вигляду YAML-процесу.

## 4.2. Головний принцип

Процес описується людською мовою як послідовність робочих кроків.

Технічна точність зберігається для:

- назв класів;
- назв атрибутів;
- status values;
- document fields;
- template IDs;
- contract IDs;
- validator IDs;
- schema names;
- artifact names;
- exact payload/query/assertion requirements.

Технічна структура процесу з YAML не переноситься майже один в один.

## 4.3. Як компілювати процес

YAML-конструкції:

- `on_answer`;
- `allowed_from`;
- `state_updates`;
- `next`;
- `gates`;
- raw transition maps;
- machine-only node metadata;

треба переформулювати у зрозумілі інструкції:

- що аналітик перевіряє;
- яке рішення приймає;
- які факти потрібні;
- що створює;
- що робить при успіху;
- що робить при помилці;
- хто виправляє;
- що інвалідується;
- коли можна продовжувати.

## 4.4. Структура model-visible файла

Рекомендовано:

- коротка мета;
- робочі етапи;
- послідовні кроки;
- окремі правила для документів;
- validation/approval/correction;
- terminal behavior.

Допускаються stable instruction IDs для traceability, але файл не повинен виглядати як YAML dump або state-machine listing.

## 4.5. Заборонено

- копіювати YAML-блоки;
- показувати transition tables;
- виводити variable dictionary процесу;
- перетворювати кожен YAML field у видимий technical paragraph;
- приховувати технічні вимоги до даних і документів;
- замінювати точні validator/contract references загальними словами.

## 4.6. Representation-specific validators

Перевіряти:

- відсутність YAML process-control blocks;
- наявність усіх required semantic units;
- правильний порядок;
- narrative readability;
- exact preservation of data/template/contract semantics;
- reachability correction loops;
- model-visible sufficiency;
- Driver-owned validator enforcement.

---

# 5. Mixed Accumulated Instructions

## 5.1. Призначення

YAML-derived процес у вигляді історично накопиченої робочої документації аналітика.

Це проміжний формат між Structured Instructions і Domain Adapted All-in-One.

## 5.2. Головний принцип

Корпус повинен виглядати так, ніби він поступово розвивався у реальній роботі:

- рання спрощена версія;
- практичні уточнення;
- QA notes;
- automation details;
- incident-driven corrections;
- late-stage rules;
- reminders;
- templates;
- troubleshooting.

Фінальний виконавець не повинен бачити або здогадуватися, що корпус:

- створено з YAML;
- синтетично стилізовано;
- є benchmark package;
- містить controlled redundancy;
- має hidden provenance mapping.

## 5.3. Model-visible corpus

У поточному підході всі робочі інструкції можуть бути зібрані у:

`MIXED_ACCUMULATED_ANALYST_INSTRUCTIONS.md`

Всередині дозволено імітувати набір різночасових внутрішніх документів або розділів, але без метаопису генерації.

## 5.4. Історична правдоподібність

Дозволяється:

- помірна надлишковість;
- різний рівень деталізації;
- різні стилі авторства;
- ранні спрощення;
- пізні уточнення;
- старі терміни у прикладах;
- incident notes;
- checklists;
- correction memos;
- uneven structure.

Орієнтир signal-to-noise:

- 70–85% корисного змісту;
- 10–20% природного повторення;
- 5–10% застарілих або спрощених формулювань, які пізніше однозначно уточнюються.

## 5.5. Apparent contradictions

Дозволені лише суперечності, які природно розв’язуються пізнішим уточненням або контекстом.

Не можна залишати два рівноправні взаємовиключні critical rules.

Наприклад:

- раннє: після перевірки документ можна погодити;
- пізнє: approval чинний лише для hash/version, підтвердженого Driver-generated receipt.

## 5.6. Приховування походження

У model-visible corpus не повинно бути:

- YAML;
- compiler rules;
- provenance;
- synthetic history;
- benchmark/evaluator metadata;
- пояснення навмисних повторів;
- опису controlled contradictions;
- generation manifest;
- traceability table до YAML nodes.

Compiler rules, provenance і validators зберігаються у package-private або build/evidence частині, але не передаються моделі як робоча документація.

## 5.7. Збереження інваріантів

Критичний інваріант бажано природно показати щонайменше у двох формах:

- workflow + checklist;
- guide + incident note;
- template + validation note;
- correction memo + approval guide.

Не копіювати формулювання механічно.

## 5.8. Representation-specific validators

Перевіряти:

- absence of origin disclosure;
- absence of machine-process reconstruction;
- historical realism;
- різноманітність section/document styles;
- natural redundancy;
- відсутність нерозв’язних critical contradictions;
- full semantic coverage;
- model-visible sufficiency;
- all critical invariants;
- Driver-owned validation;
- blind-execution readiness.

---

# 6. Domain Adapted All-in-One

## 6.1. Призначення

Майже оригінальна робоча документація аналітика, з якої прибрано або узагальнено доменну специфіку.

Це не YAML-derived реконструкція процесу.

## 6.2. Що зберігається

- природний історичний стиль;
- існуючі повтори;
- локальні суперечності;
- різна зрілість розділів;
- фактична організація оригінального корпусу;
- реальні практичні notes, templates і examples.

## 6.3. Що адаптується

- назви конкретної компанії;
- приватні назви систем;
- унікальні business entities;
- production secrets;
- доменно-специфічні значення, які роблять benchmark непереносним.

## 6.4. Заборонено

- перебудовувати корпус за YAML;
- робити його чистішим і логічнішим, ніж оригінал;
- додавати процесні правила, яких не було;
- маскувати втрату семантики новими вигаданими інструкціями.

## 6.5. Перевірки

- domain de-identification;
- preservation of original structure/style;
- absence of secret/private facts;
- no accidental YAML-derived reconstruction;
- benchmark input sufficiency;
- route behavior against the same cases.

---

# 7. Порівняльна матриця

| Тип | Процес | Дані/шаблони | Стиль | Походження |
|---|---|---|---|---|
| YAML | максимально технічний і формальний | максимально технічні | machine-readable | авторитетна формалізація |
| Structured Instructions | структурований, але prose/non-YAML | технічно точні | чистий робочий процес | компіляція з YAML |
| Mixed Accumulated | історично накопичений, нерівномірний | технічно достатні | живий evolving corpus | компіляція з YAML із прихованим походженням |
| Domain Adapted All-in-One | оригінальна природна структура | як в оригіналі після адаптації | natural legacy corpus | адаптація первинних інструкцій |

---

# 8. Спільний compilation lifecycle

Для кожного YAML-derived варіанта:

1. Зафіксувати immutable YAML source і checksum.
2. Визначити representation type.
3. Завантажити правила компіляції саме цього типу.
4. Побудувати semantic coverage map.
5. Створити model-visible corpus.
6. Зберегти compiler/provenance metadata поза model-visible boundary.
7. Запустити representation-specific validators.
8. Запустити semantic parity.
9. Перевірити Driver, contracts, templates і selected-run inputs.
10. Зібрати candidate ZIP.
11. Виконати clean-extraction black-box validation.
12. Виконати External Model Preflight Simulation з фактичним launch prompt.
13. На FAIL — patch version і повторний цикл, максимум п’ять.
14. На PASS — зафіксувати green-light evidence.
15. Лише після цього віддавати пакет на зовнішні RUN.

---

# 9. Обов’язкова External Model Preflight Simulation

Перед передачею пакета потрібно відтворити первинну перевірку так, як її виконає стороння модель:

1. взяти фінальний ZIP;
2. взяти точний launch prompt;
3. розпакувати у чистий каталог;
4. не мати доступу до build-каталогу;
5. виконати команди у порядку prompt;
6. перевірити кожен literal path;
7. не підміняти відсутній файл аналогом;
8. застосувати ті самі hard-stop/NO_CHANGE правила;
9. переконатися, що позитивний RUN доходить не лише до entrypoint, а й до першого generation gate;
10. перевірити exact bindings, fixtures, request schemas, runner contract;
11. зберегти stdout, stderr, return codes і повний журнал;
12. не видавати green light без PASS цієї симуляції.

---

# 10. Versioning

- зміна business/process semantics: minor або major;
- виправлення package/validator/launch-path без зміни семантики: patch;
- зміна representation style rules: minor;
- кожна версія має окремий manifest, checksum і analysis record;
- старі результати не переносяться на нову версію автоматично.

---

# 11. Що має бути зафіксовано у головному процесі

Модель, яка керує процесом створення playbook, повинна:

- зберігати ці правила як нормативну частину процесу;
- вимагати явний representation type;
- не використовувати універсальний compiler для всіх форматів;
- запускати representation-specific validation;
- вести evidence package;
- блокувати передачу пакета до green light;
- не оголошувати PASS лише на підставі кількості кроків або checksum-файла;
- фіксувати кожен новий клас false-positive у validation methodology.
