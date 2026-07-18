# Розділ 20. Як правильно використовувати FREEFORM

У попередньому розділі ми домовилися про важливу річ: не все в Ordo потрібно формалізувати до останнього слова.

Але з цього не випливає, що `FREEFORM` можна використовувати як місце, куди складається все незрозуміле.

Навпаки: `FREEFORM` — одна з найнебезпечніших і водночас найкорисніших частин Ordo. Вона дозволяє зберегти людський зміст там, де жорстка структура ще не потрібна або поки що неможлива. Але якщо користуватися нею без правил, Ordo дуже швидко перетвориться назад на великий prompt.

Цей розділ про те, як використовувати `FREEFORM` правильно.

## Навіщо потрібен FREEFORM

У реальних інструкціях завжди є частини, які важко або недоцільно одразу перетворити на формальні оператори.

Наприклад:

```text
- пояснення доменного контексту;
- приклади хороших і поганих відповідей;
- історія появи правила;
- стильові рекомендації;
- застереження для моделі;
- пояснення для аналітика або розробника;
- нюанси, які поки що не мають стабільної структури.
```

Якщо спробувати все це силоміць перетворити на `NODE`, `GATE`, `ASSERT.NOT` або `OUTPUT.DEF`, ми можемо втратити зміст.

Тому Ordo вводить контрольовану лазейку:

```text
FREEFORM
```

Але це не “вільний текст без правил”.

![Nebu — ідея: FREEFORM як контрольований фрагмент](../assets/mascots/64x64/Nebu_idea_64x64.png)

Правильніше думати так:

```text
FREEFORM — це контрольований фрагмент людського змісту, який має явне місце, причину, межі і привʼязку до execution context.
```

## Чим FREEFORM не є

`FREEFORM` не є способом обійти Ordo.

Погано:

```yaml
freeform: |
  Виконай весь процес створення історичної події за всіма правилами,
  постав потрібні питання, перевір усе, сформуй архів і зроби QA.
```

Такий блок фактично ховає весь процес у текст.

Модель знову отримує великий prompt і має сама здогадатися:

```text
- де початок;
- де стан;
- де рішення;
- де gate;
- де stop condition;
- що треба підтвердити;
- що можна робити без підтвердження;
- який output є правильним.
```

Це не Ordo.

У правильному Ordo `FREEFORM` не замінює execution logic. Він тільки доповнює її.

## Базове правило FREEFORM

![Nebu — увага: FREEFORM не може ховати обовʼязкові правила](../assets/mascots/64x64/Nebu_attention_64x64.png)

Головне правило:

```text
FREEFORM не може містити приховані обовʼязкові правила виконання.
```

Якщо фрагмент впливає на те, чи можна рухатися далі, він має бути винесений у формальну структуру.

Наприклад, якщо в тексті є правило:

```text
Перед створенням архіву обовʼязково перевір, що всі mandatory files існують.
```

це не має залишатися тільки в `FREEFORM`.

Це має бути `GATE`:

```yaml
- op: GATE.DEF
  id: G_ARCHIVE_MANDATORY_FILES
  condition: "all mandatory files are present"
  on_fail: "BLOCK_ARCHIVE"
```

А в `FREEFORM` можна залишити пояснення:

```yaml
freeform:
  id: FF_ARCHIVE_REASON
  binds_to: G_ARCHIVE_MANDATORY_FILES
  text: |
    Цей gate потрібний тому, що в попередніх пакетах модель іноді
    створювала архів без частини mandatory files або додавала зайві файли.
```

Тут `FREEFORM` пояснює правило, але не є самим правилом.

## Що має бути у правильному FREEFORM-блоці

Кожен `FREEFORM`-блок має мати мінімальну службову інформацію.

Я б рекомендував таку структуру:

```yaml
freeform:
  id: FF_001
  title: "Пояснення доменного контексту"
  type: "domain_explanation"
  binds_to:
    - NODE_SELECT_EVENT_PATH
    - G_EVENT_TYPE_CONFIRMED
  reason: "Потрібно зберегти людське пояснення, але воно не є окремим gate"
  text: |
    ...людський текст...
```

Тут важливі поля:

```text
id          — стабільний ідентифікатор блоку;
title       — коротка назва;
type        — тип freeform-змісту;
binds_to    — до чого цей текст привʼязаний;
reason      — чому текст залишений у freeform;
text        — сам зміст.
```

Без `binds_to` модель не розуміє, де саме цей текст застосовується.

Без `reason` незрозуміло, чому це не було формалізовано.

Без `type` неможливо оцінювати покриття і якість `FREEFORM` у великому playbook-у.

## Типи FREEFORM

Не всі `FREEFORM`-блоки однакові.

Корисно одразу розрізняти їх за типами.

Наприклад:

```text
1. domain_explanation
   Доменне пояснення, яке допомагає моделі зрозуміти предметну область.

2. rationale
   Пояснення, чому правило або gate існує.

3. example
   Приклад правильного або неправильного виконання.

4. style_guidance
   Рекомендації щодо стилю, тону або рівня деталізації.

5. migration_note
   Пояснення, як стара інструкція була перенесена в Ordo.

6. analyst_note
   Примітка для аналітика або людини, яка керує процесом.

7. unresolved_design
   Усвідомлено залишена відкрита частина, яку треба формалізувати пізніше.
```

Це допомагає не змішувати все в один великий текстовий блок.

## FREEFORM має бути привʼязаний до execution context

Поганий `FREEFORM` живе сам по собі.

```yaml
freeform:
  text: |
    У цій системі важливо не пропускати перевірки і не створювати
    фінальний пакет без погодження аналітика.
```

Цей текст правильний за змістом, але Ordo не знає, де його застосувати.

Краще:

```yaml
freeform:
  id: FF_APPROVAL_CONTEXT
  type: rationale
  binds_to:
    - G_ANALYST_APPROVAL_BEFORE_ARCHIVE
    - G_NO_ARCHIVE_BEFORE_VALIDATION
  reason: "Пояснює причину двох approval gates"
  text: |
    У цій системі фінальний пакет не можна створювати автоматично,
    тому що аналітик має підтвердити бізнесову і технічну готовність
    перед handoff.
```

Тепер текст має місце в процесі.

## FREEFORM не повинен мати власного прихованого статусу

Ще одна типова помилка — написати в `FREEFORM` щось таке:

```text
Якщо користувач погодився, вважай пакет готовим до архіву.
```

Це фактично статусна логіка.

Вона має бути в `STATUS.SEMANTICS` або gate transition.

Правильно:

```yaml
status_semantics:
  ready_for_archive:
    allowed_when:
      - G_ANALYST_APPROVAL_PASSED
      - G_VALIDATION_PASSED
      - G_CONSISTENCY_CHECK_PASSED
```

А `FREEFORM` може пояснити:

```yaml
freeform:
  id: FF_READY_FOR_ARCHIVE_EXPLANATION
  type: rationale
  binds_to:
    - ready_for_archive
  text: |
    Статус ready_for_archive означає не просто “користувач сказав ок”,
    а що пройдено всі формальні approval і validation gates.
```

## FREEFORM не повинен створювати нові outputs

Якщо в тексті сказано:

```text
Також підготуй короткий summary для менеджера.
```

це не має бути тільки у `FREEFORM`.

Це output contract.

Правильно:

```yaml
outputs:
  - id: OUT_MANAGER_SUMMARY
    type: document
    required: true
    audience: "manager"
```

А `FREEFORM` може описати стиль цього summary:

```yaml
freeform:
  id: FF_MANAGER_SUMMARY_STYLE
  type: style_guidance
  binds_to:
    - OUT_MANAGER_SUMMARY
  text: |
    Summary має бути коротким, без зайвих технічних деталей,
    з акцентом на ризик, рішення і наступну дію.
```

## FREEFORM і приклади

Приклади — одна з найкращих причин використовувати `FREEFORM`.

Приклад часто важко формалізувати без втрати користі.

Наприклад:

```yaml
freeform:
  id: FF_GOOD_BAD_GATE_EXAMPLES
  type: example
  binds_to:
    - G_OUTPUT_READY
  text: |
    Погано:
    “Перевір, що все нормально.”

    Добре:
    “Перевір, що всі mandatory sections присутні,
    статуси не суперечать один одному,
    validation report має passed або passed_with_notes,
    а unresolved items явно перелічені.”
```

Такий `FREEFORM` не керує процесом напряму, але допомагає моделі краще виконати формальні правила.

## FREEFORM і людський стиль

Стильові інструкції часто краще тримати у `FREEFORM`, якщо вони не є критичними validation rules.

Наприклад:

```yaml
freeform:
  id: FF_PM_STYLE
  type: style_guidance
  binds_to:
    - OUT_JIRA_TASK
  text: |
    Пиши задачу рівнем PM: без зайвих деталей реалізації,
    але з достатньою конкретикою для прийняття задачі в роботу.
```

Але якщо стильова вимога стає критичною забороною, її треба дублювати як `ASSERT.NOT`.

Наприклад:

```yaml
assert_not:
  - id: A_NO_INTERNAL_IMPLEMENTATION_DETAILS
    target: OUT_JIRA_TASK
    rule: "Output must not include internal implementation details"
```

Тоді `FREEFORM` пояснює тон, а `ASSERT.NOT` блокує помилку.

## FREEFORM і міграція старих playbook-ів

Під час міграції великих markdown playbook-ів в Ordo майже завжди частина тексту спочатку потрапляє у `FREEFORM`.

Це нормально.

Ненормально — залишити все в `FREEFORM` і назвати це міграцією.

Правильний процес такий:

```text
1. Розділити старий текст на фрагменти.
2. Витягнути формальні правила.
3. Перенести рішення в NODE / PATH / STATE.
4. Перенести перевірки в GATE / ASSERT.NOT.
5. Перенести outputs в OUTPUT.DEF.
6. Те, що залишилось, оформити як controlled FREEFORM.
7. Для кожного FREEFORM-блоку пояснити, чому він не формалізований.
8. Пізніше переглянути coverage і поступово зменшувати зайвий FREEFORM.
```

Тобто `FREEFORM` — це не смітник, а тимчасова або усвідомлена зона змісту.

## Ознаки неправильного FREEFORM

Є кілька простих ознак, що `FREEFORM` використовується неправильно.

### Ознака 1. У FREEFORM є слова “обовʼязково”, “заборонено”, “не можна”

Якщо в тексті є:

```text
обовʼязково перевір;
заборонено створювати;
не можна переходити;
потрібно отримати підтвердження;
```

найімовірніше, це не має залишатися тільки в `FREEFORM`.

Це кандидат на `GATE`, `ASSERT.NOT`, `APPROVAL.REQUIRE` або `STATUS.SEMANTICS`.

### Ознака 2. FREEFORM визначає порядок кроків

Якщо блок описує послідовність:

```text
спочатку зроби A, потім B, після цього C, а якщо D — перейди до E
```

це не просто пояснення.

Це execution path.

Його треба формалізувати.

### Ознака 3. FREEFORM створює новий документ

Якщо freeform-блок каже:

```text
також створи окремий README
```

це output definition.

### Ознака 4. FREEFORM змінює значення статусу

Якщо блок каже:

```text
цей статус означає, що можна запускати пакет у роботу
```

це status semantics.

### Ознака 5. FREEFORM дозволяє обійти gate

Якщо блок каже:

```text
у простих випадках можна пропустити цю перевірку
```

це override rule.

Воно має бути явним.

## Як вирішити: формалізувати чи залишити FREEFORM

Можна використовувати просте дерево рішень.

```text
Питання 1: Чи цей фрагмент змінює шлях виконання?
Так → формалізувати.
Ні → питання 2.

Питання 2: Чи цей фрагмент блокує або дозволяє перехід?
Так → gate/status/approval.
Ні → питання 3.

Питання 3: Чи цей фрагмент визначає обовʼязковий output?
Так → OUTPUT.DEF.
Ні → питання 4.

Питання 4: Чи цей фрагмент забороняє помилкову поведінку?
Так → ASSERT.NOT.
Ні → питання 5.

Питання 5: Чи цей фрагмент пояснює, навчає, дає приклад або стиль?
Так → controlled FREEFORM.
Ні → можливо, фрагмент зайвий.
```

## Приклад: неправильний і правильний варіант

Поганий варіант:

```yaml
freeform:
  text: |
    Перед фінальним архівом перевір, що всі файли є,
    що validation report успішний,
    що consistency check не має критичних помилок,
    і що користувач погодив фінальний пакет.
```

Цей текст містить кілька gate-ів.

Краще:

```yaml
gates:
  - id: G_FILES_PRESENT
    condition: "mandatory files exist"
    on_fail: "BLOCK_ARCHIVE"

  - id: G_VALIDATION_PASSED
    condition: "validation report is passed or passed_with_notes"
    on_fail: "BLOCK_ARCHIVE"

  - id: G_CONSISTENCY_PASSED
    condition: "consistency check has no critical errors"
    on_fail: "BLOCK_ARCHIVE"

  - id: G_USER_APPROVAL_RECEIVED
    condition: "user approved final package"
    on_fail: "WAIT_FOR_APPROVAL"

freeform:
  id: FF_ARCHIVE_GATE_RATIONALE
  type: rationale
  binds_to:
    - G_FILES_PRESENT
    - G_VALIDATION_PASSED
    - G_CONSISTENCY_PASSED
    - G_USER_APPROVAL_RECEIVED
  text: |
    Ці gate-и існують тому, що фінальний архів є handoff-артефактом.
    Якщо він неповний або неперевірений, наступний учасник процесу
    отримає помилкову основу для роботи.
```

Тепер execution logic формальна, а пояснення збережене.

## FREEFORM має бути видимим у звіті

Якщо Ordo-програма містить `FREEFORM`, це має бути видно у validation або coverage report.

Наприклад:

```json
{
  "freeform_coverage": {
    "total_blocks": 12,
    "bound_blocks": 12,
    "unbound_blocks": 0,
    "blocks_with_reason": 12,
    "high_risk_blocks": 2,
    "recommendation": "review high-risk freeform blocks for future formalization"
  }
}
```

Це дозволяє бачити, чи `FREEFORM` справді контрольований.

Якщо в playbook-у 40% змісту залишилось у `FREEFORM`, це може бути нормально для першої міграції.

Але тоді треба чесно сказати:

```text
structured_core: 60%
controlled_freeform: 40%
```

І додати план, що саме варто формалізувати пізніше.

## Високоризиковий FREEFORM

Не всі freeform-блоки однаково безпечні.

Високоризиковими є блоки, які:

```text
- містять слова “must”, “required”, “forbidden”, “block”, “approve”;
- описують послідовність дій;
- стосуються фінального handoff;
- стосуються юридичних, фінансових або комплаєнс-рішень;
- містять правила створення або видалення даних;
- містять правила запуску зовнішніх інструментів;
- визначають, коли можна вважати процес завершеним.
```

Такі блоки треба або формалізувати, або явно позначити як ризикові.

Наприклад:

```yaml
freeform:
  id: FF_LEGACY_QA_NOTE
  type: unresolved_design
  risk_level: high
  binds_to:
    - QA_PACKAGE_GENERATION
  reason: "Legacy QA description is not yet fully formalized"
  action_required: "Convert to GATE.DEF and OUTPUT.DEF in next version"
  text: |
    ...старий QA-текст...
```

Це чесніше, ніж робити вигляд, що все вже стало формальною Ordo-програмою.

## FREEFORM як борг формалізації

Іноді `FREEFORM` — це не фінальне рішення, а борг.

Це нормально, якщо борг видимий.

Для цього можна використовувати поле:

```yaml
formalization_status: "accepted_for_now"
```

або:

```yaml
formalization_status: "candidate_for_next_version"
```

Наприклад:

```yaml
freeform:
  id: FF_COMPLEX_DOMAIN_RULES
  type: unresolved_design
  formalization_status: "candidate_for_next_version"
  reason: "Domain rules are not stable enough yet"
```

Так Ordo дозволяє розвивати мову поступово.

Ми не вимагаємо миттєвої ідеальної формалізації. Але ми вимагаємо чесності: що формалізовано, що ні, і чому.

## Як модель має працювати з FREEFORM

![Nebu — подумати: формальна структура має пріоритет над FREEFORM](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Модель не повинна сприймати `FREEFORM` як вільний дозвіл робити що завгодно.

Правильна поведінка моделі:

```text
1. Прочитати FREEFORM-блок.
2. Подивитися, до чого він привʼязаний.
3. Визначити його тип.
4. Перевірити, чи він не містить прихованих gate/rule/output/status.
5. Використати його тільки в межах binds_to.
6. Якщо блок суперечить формальній структурі — формальна структура має пріоритет.
7. Якщо суперечність критична — зупинитися і повідомити про conflict.
```

Наприклад, якщо `GATE.DEF` забороняє створювати архів без approval, а `FREEFORM` десь натякає, що “у простих випадках можна одразу сформувати пакет”, модель не має обирати зручний варіант.

Вона має сказати:

```text
CONFLICT.DETECTED:
FREEFORM suggests possible shortcut, but formal gate requires approval.
Execution blocked until conflict is resolved.
```

## Пріоритет формальної структури

У Ordo треба закласти просту ієрархію.

```text
1. Formal execution contract
2. Gates / assertions / status semantics
3. Output definitions
4. Domain pack rules
5. Controlled FREEFORM
6. Style notes / examples
```

`FREEFORM` не може переписувати `GATE`.

`FREEFORM` не може створювати непогоджений output.

`FREEFORM` не може змінювати status semantics.

`FREEFORM` може пояснювати, уточнювати і навчати.

## Міні-вправа

Візьміть такий фрагмент:

```text
Після підготовки пакета перевір, що README, Jira task, QA package і validation report існують. Не створюй архів, якщо validation report має critical errors. У відповіді аналітику поясни коротко, що саме готово, а що потребує уваги. Пиши українською мовою, без зайвих англіцизмів.
```

Розкладіть його на частини.

Що тут має бути `GATE`?

```text
- перевірка mandatory files;
- заборона створення архіву при critical errors;
```

Що має бути `OUTPUT.DEF`?

```text
- відповідь аналітику з коротким summary;
```

Що має бути `ASSERT.NOT`?

```text
- не створювати архів при critical errors;
```

Що можна залишити як `FREEFORM`?

```text
- пояснення стилю відповіді;
- рекомендація писати українською без зайвих англіцизмів;
```

Після цього спробуйте оформити один `FREEFORM`-блок із полями:

```text
id
type
binds_to
reason
text
```

## Короткий підсумок

`FREEFORM` потрібний Ordo, бо реальні людські інструкції не завжди можна одразу повністю формалізувати.

Але `FREEFORM` має бути контрольованим.

Правильний `FREEFORM`:

```text
- має id;
- має тип;
- має reason;
- має binds_to;
- не приховує gate-и;
- не створює outputs;
- не змінює statuses;
- не обходить approvals;
- не суперечить формальній структурі;
- відображається в coverage report.
```

Найкоротше правило:

```text
FREEFORM може пояснювати виконання, але не повинен керувати виконанням замість Ordo.
```

Саме тому `FREEFORM` — це не слабкість Ordo, а спосіб чесно працювати з тією частиною людського знання, яка ще не стала формальною мовою.
