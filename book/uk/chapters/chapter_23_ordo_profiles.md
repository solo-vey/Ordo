# Розділ 23. Ordo Profiles

## Навіщо потрібні Profiles

У попередньому розділі ми розібрали `Ordo Core` — мінімальний набір конструкцій, без яких Ordo-програма не може бути керованою. Core відповідає за базову форму виконання: entry, node, state, gate, output, trace.

Але в реальній роботі цього недостатньо.

Одна Ordo-програма може створювати аналітичний пакет. Інша — вести користувача через guided intake. Третя — формувати QA-документацію. Четверта — перевіряти rendered artifact. Пʼята — працювати з approvals, доказами, шаблонами й каталогом документів.

Усі ці сценарії використовують Core, але потребують різних додаткових правил.

Саме для цього в Ordo потрібні `Profiles`.

Простими словами:

```text
Ordo Profile — це стандартний набір додаткових правил і конструкцій для певного типу роботи.
```

![Nebu — ідея: Profile як режим роботи](../assets/mascots/64x64/Nebu_idea_64x64.png)

Core каже: “будь-яка Ordo-програма має мати кероване виконання”.

Profile каже: “як саме керувати виконанням у конкретному класі задач”.

## Чому не можна все покласти в Core

Може здатися, що всі корисні правила треба одразу додати в Core. Наприклад:

```text
- правила для документів;
- правила для QA;
- правила для approvals;
- правила для rendered artifact validation;
- правила для evidence matrix;
- правила для розбиття документації на файли;
- правила для package generation.
```

Але тоді Core швидко стане занадто великим.

Core має залишатися мінімальним і стабільним. Він не повинен знати всі можливі типи задач. Інакше Ordo втратить гнучкість.

Тому Ordo розділяє:

```text
Core     → базова мова виконання
Profile  → типовий режим роботи
Domain   → конкретна предметна область
Library  → reusable готові частини
```

![Nebu — подумати: розділення Core, Profile, Domain і Library](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Це схоже на звичайне програмування. У мові є базовий синтаксис, але для web, тестів, баз даних або UI використовуються окремі фреймворки й бібліотеки.

В Ordo Profile виконує роль такого стандартного режиму роботи для певного класу задач.

## Що може входити в Profile

Profile може містити не все підряд, а тільки ті правила, які повторюються в багатьох Ordo-програмах одного типу.

Наприклад, Documentation Profile може містити:

```text
- правила роботи з шаблонами;
- правила розбиття великих документів;
- правила вибору потрібних документів;
- правила перевірки готового rendered artifact;
- правила catalog / selected docs;
- правила self-check перед handoff.
```

QA Profile може містити:

```text
- структуру test case;
- правила fixture;
- expected behavior;
- негативні сценарії;
- regression suite;
- coverage report;
- manual QA runbook rules.
```

Approval Profile може містити:

```text
- що саме потребує підтвердження людини;
- які gates є blocking;
- які рішення модель не має права приймати сама;
- як фіксувати approval у state;
- як заборонити фінальний output без approval.
```

Тобто Profile — це не предметна область. Це стиль і режим виконання.

## Приклад: Documentation Profile

Уявімо, що ми маємо Ordo-програму, яка створює пакет документів.

Без Profile інструкція може виглядати так:

```text
Створи README, паспорт, задачу, QA-документ і validation report.
Перед архівом перевір, що все консистентно.
```

Це зрозуміло людині, але для керованого виконання такому опису бракує структури.

Documentation Profile може формалізувати це так:

```yaml
profile:
  id: "ordo.profile.documentation"
  version: "0.1"

rules:
  - id: "DOC.CATALOG"
    description: "усі документи пакета мають бути зареєстровані в каталозі"

  - id: "DOC.SELECT"
    description: "перед відповіддю модель має визначити, які документи потрібні для поточного кроку"

  - id: "TEMPLATE.BIND"
    description: "кожен output-документ має бути привʼязаний до шаблону або явно описаної структури"

  - id: "RENDER.VALIDATE"
    description: "перевіряти потрібно не тільки шаблон, а фінальний rendered artifact"
```

Тепер будь-яка Ordo-програма, яка підключає цей Profile, отримує стандартні правила документаційного виконання.

## Profile як контракт поведінки

![Nebu — увага: Profile змінює контракт виконання](../assets/mascots/64x64/Nebu_attention_64x64.png)

Profile не просто додає корисні поради. Він змінює execution contract.

Якщо Ordo-програма підключила Documentation Profile, модель уже не може працювати так, ніби вона просто пише текст.

Вона має:

```text
- знати, які документи існують;
- вибирати релевантні документи для кроку;
- не змішувати шаблон і rendered artifact;
- не створювати фінальний пакет без self-check;
- фіксувати, які документи були використані;
- повідомляти про missing required artifact;
- виконувати validation gates.
```

Це важлива різниця.

У звичайному prompt-і можна написати: “перевір консистентність”.

У Profile можна сказати: “консистентність є обовʼязковим gate перед handoff”.

## Profile у Ordo Source

У людському Ordo Source підключення Profile може виглядати так:

```yaml
ordo:
  version: "0.11"

profiles:
  use:
    - id: "ordo.profile.documentation"
      version: "0.1"
    - id: "ordo.profile.qa"
      version: "0.1"
    - id: "ordo.profile.approval"
      version: "0.1"
```

Така програма одразу повідомляє:

```text
це не просто генерація тексту;
це документаційний процес;
він має QA-структуру;
частина рішень потребує людського approval.
```

## Profile у compiled IR

У compiled IR це може перетворитися на набір operations:

```json
[
  {
    "op": "PROFILE.USE",
    "id": "P1",
    "profile": "ordo.profile.documentation",
    "version": "0.1"
  },
  {
    "op": "PROFILE.USE",
    "id": "P2",
    "profile": "ordo.profile.qa",
    "version": "0.1"
  },
  {
    "op": "PROFILE.BIND_RULES",
    "id": "P3",
    "profiles": ["P1", "P2"]
  }
]
```

Після цього компілятор або runtime має знати, що в програмі активні додаткові правила.

Наприклад, якщо Documentation Profile активний, тоді final package generation не може відбутися без `RENDER.VALIDATE` або еквівалентного gate.

## Типові Profile-конструкції

У поточній концепції Ordo можна виділити такі Profile-level конструкції:

```text
TEMPLATE.BIND
EVIDENCE.MATRIX
APPROVAL.REQUIRE
DOC.SPLIT
DOC.CATALOG
DOC.SELECT
RENDER.VALIDATE
QA.CASE.DEF
QA.RUNBOOK.DEF
PACKAGE.SELF_CHECK
HANDOFF.NOTE
```

Це не обовʼязково повний список. Але він показує різницю між Core і Profile.

Core каже:

```text
має бути gate
```

Profile каже:

```text
перед архівом має бути rendered artifact validation gate
```

Core каже:

```text
має бути output
```

Profile каже:

```text
output має відповідати template binding і входити в document catalog
```

Core каже:

```text
має бути state
```

Profile каже:

```text
state має містити approval status, selected docs і validation result
```

## Profile і Domain Pack

Profile часто плутають із Domain Pack. Це треба розділити дуже чітко.

Profile відповідає на питання:

```text
який це тип процесу?
```

Domain Pack відповідає на питання:

```text
про яку предметну область цей процес?
```

Наприклад, History Event Playbook може використовувати:

```text
Documentation Profile
QA Profile
Approval Profile
Debug/Test Profile
History Event Domain Pack
```

Profile дає загальні правила документів, QA і approval.

Domain Pack дає специфіку історичних подій:

```text
- Path A1/A2/A3/A4/A5;
- HistoryEvent;
- ChangeRecord;
- source row;
- no-op rules;
- event alias;
- history event package structure.
```

Це різні рівні.

Якщо їх змішати, Ordo-програма стане важкою для підтримки.

## Profile і бібліотеки

Пізніше в книзі ми окремо поговоримо про Ordo Libraries. Але вже тут варто зафіксувати різницю.

Profile — це стандартний режим поведінки.

Library — це reusable пакет готових частин.

Наприклад:

```text
ordo.profile.qa
```

може визначати, що в QA-процесі мають бути fixtures, expected behavior і regression suite.

А бібліотека:

```text
ordo.library.qa.history_event_basic_tests
```

може містити готові test cases для конкретного типу History Event.

Тобто Profile задає правила гри, а Library може дати готові reusable елементи для цієї гри.

## Чому Profiles важливі для компілятора

Компілятор Ordo має розуміти активні Profiles.

Без цього він не зможе правильно перевірити програму.

Наприклад, якщо активний QA Profile, компілятор може вимагати:

```text
- наявність TEST.DEF;
- наявність хоча б мінімального coverage report;
- наявність negative test для blocking gates;
- наявність expected behavior для ключових paths.
```

Якщо активний Documentation Profile, компілятор може перевіряти:

```text
- чи всі required documents описані;
- чи є document catalog;
- чи є validation report;
- чи не створюється archive до self-check;
- чи rendered artifact validation не замінена перевіркою шаблону.
```

Таким чином Profile — це ще й механізм compiler validation.

## Типові помилки

### Помилка 1. Робити Profile занадто предметним

Погано:

```text
Profile для зміни статутного капіталу компанії
```

Це вже domain pack або library, а не Profile.

Profile має бути ширшим:

```text
Documentation Profile
QA Profile
Approval Profile
Guided Intake Profile
```

### Помилка 2. Класти всі правила в Core

Якщо все зробити Core, Core стане непідйомним.

Core має бути малим. Profiles мають розширювати його для типових режимів роботи.

### Помилка 3. Не вказувати активний Profile

Якщо Ordo-програма фактично працює як QA-процес, але не підключає QA Profile, компілятор не зможе вимагати потрібні тести.

Погано:

```text
десь у тексті написано, що треба перевірити QA
```

Добре:

```yaml
profiles:
  use:
    - id: "ordo.profile.qa"
      version: "0.1"
```

### Помилка 4. Змішувати Profile і Library

Profile не повинен бути складом готових прикладів на всі випадки.

Для reusable готових частин потрібні libraries.

Profile має задавати правила, обовʼязки і gates.

## Міні-вправа

Візьміть будь-який складний процес, який ви хочете виконувати через AI-модель.

Наприклад:

```text
- створення аналітичного пакета;
- перевірка документа;
- підготовка QA-інструкцій;
- guided intake нової задачі;
- review змін у коді;
- формування handoff для розробника.
```

Спробуйте відповісти:

```text
1. Який Core тут потрібен?
2. Який це тип процесу?
3. Який Profile найкраще підходить?
4. Чи потрібен Documentation Profile?
5. Чи потрібен QA Profile?
6. Чи потрібен Approval Profile?
7. Які gates має додати Profile?
8. Які перевірки має виконувати компілятор?
9. Що тут є domain-specific і не має потрапити в Profile?
```

Якщо ви можете відповісти на ці питання, ви вже починаєте мислити не prompt-ами, а шарами Ordo.

## Короткий підсумок

`Ordo Profile` — це стандартний набір додаткових правил для певного типу Ordo-процесу.

Core задає базову мову виконання.

Profile задає режим роботи.

Domain Pack задає предметну область.

Library дає reusable готові частини.

Правильне розділення цих рівнів дозволяє Ordo залишатися одночасно простою, розширюваною і придатною для великих playbook-ів.

Без Profiles кожен складний playbook буде сам винаходити правила документації, QA, approval і validation.

З Profiles ці правила стають повторно використовуваними і зрозумілими для компілятора.

<!-- REVIEWED: chapter 23; Nebu markers checked -->

