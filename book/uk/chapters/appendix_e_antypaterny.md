# Додаток E. Антипатерни

Антипатерн — це підхід, який здається зручним або швидким, але в реальній роботі робить Ordo-програму менш керованою, менш перевірюваною або менш безпечною.

Цей додаток не замінює повну перевірку playbook-а. Його зручно використовувати як швидкий список типових помилок перед тим, як віддавати Ordo-програму в роботу, публікувати library або збирати фінальний package.

## E.1. Великий prompt замість Ordo-програми

### Ознака

Уся логіка описана одним великим текстом без явних `intent`, `contract`, `state`, `node`, `gate`, `output` і `handoff`.

### Чому це проблема

Модель може виконати частину інструкції, пропустити важливий gate, переплутати приклад із правилом або перейти до фінального результату раніше, ніж процес справді готовий.

### Як виправити

Розбити інструкцію на явні частини:

```text
intent → contract → context → state → path → steps → gates → result → handoff
```

## E.2. Контракт прихований у тексті

### Ознака

У тексті є фрази на кшталт “очевидно”, “за потреби”, “якщо все готово”, але не визначено, хто і як підтверджує готовність.

### Чому це проблема

Модель починає сама вирішувати, що вже підтверджено, навіть якщо користувач цього не підтверджував.

### Як виправити

Оформити контракт явно через `CONTRACT.DEF`, `ANSWER.REGISTRY`, `APPROVAL.REQUIRE` і blocking gates.

## E.3. Gate як порада

### Ознака

Gate описаний у стилі “бажано перевірити”, але після failed gate процес усе одно може рухатися далі.

### Чому це проблема

Такий gate не контролює виконання. Він лише прикрашає документацію.

### Як виправити

Для критичних перевірок використовувати blocking gate:

```text
if gate.failed → stop / ask / repair / no handoff
```

## E.4. Відсутність `ASSERT.NOT`

### Ознака

Ordo-програма описує, що потрібно зробити, але не описує, чого робити не можна.

### Чому це проблема

Модель може створити зайвий файл, придумати відсутнє значення, пропустити approval або згенерувати фінальний package у ситуації, де мала зупинитися.

### Як виправити

Додати негативні перевірки:

```text
ASSERT.NOT final_output_before_approval
ASSERT.NOT invented_source_row
ASSERT.NOT hidden_required_gate_inside_freeform
```

## E.5. FREEFORM як смітник

### Ознака

У `FREEFORM` кладуть усе, що було складно формалізувати: gates, правила, status semantics, approval logic, templates, заборони.

### Чому це проблема

FREEFORM перестає бути контрольованою лазівкою і стає місцем, де ховається справжня логіка виконання.

### Як виправити

У `FREEFORM` залишати тільки те, що справді не варто формалізувати на цьому етапі. Критичні правила переносити в `GATE.DEF`, `ASSERT.NOT`, `STATUS.SEMANTICS`, `OUTPUT.DEF` або library.

## E.6. Невидимі імпорти бібліотек

### Ознака

Ordo-програма користується правилами або шаблонами з library, але це не зазначено через `include`, `import` або `use`.

### Чому це проблема

Незрозуміло, звідки взялося правило, яка версія бібліотеки використана і хто відповідає за зміну поведінки.

### Як виправити

Усі бібліотеки підключати явно:

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
    as: "contract_first"
```

## E.7. Override без дозволу

### Ознака

Profile, Domain Pack або Library мовчки переписує gate, status або output rule, визначений в іншому шарі.

### Чому це проблема

Зміна поведінки стає невидимою. Старі тести можуть ламатися без очевидної причини.

### Як виправити

Будь-який override має бути явним, із причиною і trace:

```yaml
override:
  allow:
    - target: "G_PRE_ARCHIVE_APPROVAL"
      reason: "domain pack requires stricter approval gate"
```

## E.8. Тестування тільки фінального тексту

### Ознака

Тести перевіряють лише те, що модель видала в кінці, але не перевіряють path, state, gates, no-op і заборонені дії.

### Чому це проблема

Модель може отримати правильний результат неправильним шляхом. У production playbook-ах це небезпечно.

### Як виправити

Тестувати поведінку:

```text
EXPECT.PATH
EXPECT.STATE
EXPECT.GATE
EXPECT.OUTPUT
EXPECT.NOOP
EXPECT.NOT
```

## E.9. Відсутність debug trace

### Ознака

Коли Ordo-програма поводиться неправильно, немає запису, який path був обраний, які paths відхилені, які gates пройдені, які знання використані.

### Чому це проблема

Неможливо зрозуміти, що саме зламалося: інструкція, domain rule, library, fixture, compiler або поведінка моделі.

### Як виправити

Для складних Ordo-програм запускати `debug` або `test` mode і зберігати:

```text
TRACE.LOG
DECISION.LOG
PATH.EXPLAIN
STATE.DIFF
GATE.REPORT
KNOWLEDGE.TRACE
```

## E.10. Feedback губиться в чаті

### Ознака

Користувач вказує на проблему або покращення, але це залишається тільки в діалозі й не перетворюється на structured improvement record.

### Чому це проблема

Одна й та сама проблема повторюється. Інструкції покращуються випадково, без backlog, тестів і changelog.

### Як виправити

Використовувати `Feedback & Improvement Loop`:

```text
FEEDBACK.CAPTURE
→ ISSUE.RECORD
→ ROOT_CAUSE.LINK
→ PATCH.SUGGEST
→ TEST.SUGGEST
→ human approval
→ regression run
```

## E.11. All-in-one як source of truth

### Ознака

Великий зібраний markdown-файл редагують напряму, а окремі source-файли залишаються застарілими.

### Чому це проблема

Збірка перестає бути відтворюваною. Різні версії документації починають суперечити одна одній.

### Як виправити

Вважати source-of-truth окремі документи:

```text
section files / chapter files / domain pack files → all-in-one → PDF / archive
```

## E.12. Перевірка шаблону замість готового артефакту

### Ознака

Перевірено template або markdown-source, але не перевірено фактичний PDF, архів, Jira task або інший зібраний output.

### Чому це проблема

Помилка може зʼявитися саме на етапі render або package generation: зламане посилання, відсутній файл, неправильний порядок, незакритий кодовий блок, некоректна нумерація.

### Як виправити

Додавати `RENDER.VALIDATE` і перевіряти фактичний результат перед handoff.

## E.13. “Модель сама здогадається”

### Ознака

Автор не описує явно path selection, gates, outputs або exceptions, бо вважає, що модель “і так зрозуміє”.

### Чому це проблема

Чим складніший процес, тим дорожчі неправильні припущення моделі.

### Як виправити

Усе, що має значення для виконання, має бути явно представлене у Source або IR. Якщо щось не формалізовано, це має бути контрольований `FREEFORM`, а не мовчазне припущення.

## E.14. Занадто великий Core

### Ознака

У Core починають додавати domain-specific правила, шаблони конкретних документів або правила окремого продукту.

### Чому це проблема

Core втрачає універсальність. Мова стає важкою для підтримки й погано переноситься між доменами.

### Як виправити

Тримати Core мінімальним, а спеціалізацію виносити у Profiles, Domain Packs і Libraries.

## E.15. Немає межі відповідальності між моделлю і runner-ом

### Ознака

Незрозуміло, що саме вирішує модель, що контролює helper-runner, а що має підтвердити людина.

### Чому це проблема

Гейт може бути пропущений, output може бути створений без approval, а trace не покаже, хто саме дозволив перехід.

### Як виправити

Явно розділити відповідальність:

```text
model → semantic work
runner → process control / gates / state / tests
human → approval / governance / final decisions
```

## E.16. Короткий чек перед handoff

Перед тим як віддавати Ordo-програму або package, варто швидко перевірити:

```text
- Чи є явний intent?
- Чи є contract?
- Чи не сховані gates у FREEFORM?
- Чи є blocking gates перед фінальним output?
- Чи є ASSERT.NOT для заборонених дій?
- Чи всі libraries підключені явно?
- Чи є debug/test режим для складної логіки?
- Чи є regression suite?
- Чи feedback перетворюється на improvement records?
- Чи перевірено фактичний rendered artifact?
```

Головне правило:

```text
Якщо поведінку не можна пояснити, перевірити і відтворити, це ще не Ordo-програма, а лише добре написаний prompt.
```

---

## E.12. False deterministic gate

### Ознака

Gate виглядає як звичайна контрольна точка, але не має `method`, або semantic judgement подано так, ніби це mechanical check.

### Чому це проблема

Користувач бачить `status: passed` і не розуміє, що один gate був перевірений кодом, а інший — оцінений моделлю.

### Як виправити

Кожен gate має мати `method` і `trust_class`:

```yaml
gate:
  id: G_NO_UNSUPPORTED_FACTS
  method: self_verification
  trust_class: model_judgment
```

## E.13. Gate без `method`

### Ознака

У програмі є `GATE.DEF` або `GATE.CHECK`, але не вказано спосіб перевірки.

### Чому це проблема

Автор playbook-а не зробив явний вибір між mechanical, model judgement і human decision.

### Як виправити

У v0.12 відсутній `gate.method` має бути compilation error.

## E.14. Trace без `trace_source`

### Ознака

Debug trace показує selected path, state diff і gate report, але не вказує, чи це runtime log, hybrid trace або model self-report.

### Чому це проблема

Trace може створити завищену довіру до пояснення моделі.

### Як виправити

Додавати:

```yaml
trace_source: model_self_report | runtime_enforced | hybrid
```

## E.15. Chat-only режим подано як full runtime

### Ознака

Процес виконується в чаті без зовнішнього runner-а, але документація описує gates так, ніби вони примусово виконуються кодом.

### Чому це проблема

У `chat_internal` код може перевірити gate, але модель усе ще вирішує, коли саме запустити перевірку.

### Як виправити

Явно вказувати:

```yaml
execution_mode: chat_internal
```

і не плутати його з:

```yaml
execution_mode: full_runtime
```

## E.16. Заборона продубльована вручну у трьох місцях

### Ознака

Одна й та сама заборона окремо описана як `ASSERT.NOT`, negative gate і `EXPECT.NOT`.

### Чому це проблема

Рано чи пізно один із трьох записів буде оновлений, а інші — ні.

### Як виправити

Описувати заборону один раз як `ASSERTION`, а далі розгортати її через projection.

## E.17. Відсутній fallback для unmatched input

### Ознака

`NODE.DEF` має `allowed_answers`, але не має `on_unmatched_input`.

### Чому це проблема

Коли користувач відповідає неочікувано, модель повертається до імпровізації.

### Як виправити

Додати:

```yaml
on_unmatched_input:
  action: CLARIFY.REQUEST
  strategy: rephrase_and_narrow
  max_attempts: 2
```

## E.18. Локальні IDs у feedback records

### Ознака

Improvement record посилається на `G1` або `N2`, але не вказує, з якого шару або бібліотеки цей ID.

### Чому це проблема

У складній системі `G1` може існувати в Core, Profile, Domain Pack і Library одночасно.

### Як виправити

У feedback, trace і reports використовувати тільки повні namespaced IDs.

## E.19. Floating library version

### Ознака

Library підключена без версії або з надто широкою версією для strict-процесу.

### Чому це проблема

Поведінка програми може змінитися без зміни source-файлу.

### Як виправити

Фіксувати version policy і не використовувати floating versions у critical / strict workflows.

## E.20. FREEFORM ніколи не дозріває

### Ознака

Один і той самий FREEFORM-блок постійно породжує feedback incidents, але не формалізується.

### Чому це проблема

FREEFORM перетворюється на постійну сіру зону.

### Як виправити

Додати maturity lifecycle:

```yaml
freeform:
  maturity: candidate_for_formalization
  incident_count: 3
  incident_threshold: 3
```

і створити `FREEFORM_FORMALIZATION_RECOMMENDED`.

