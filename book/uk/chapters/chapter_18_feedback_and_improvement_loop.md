# Розділ 18. Feedback & Improvement Loop

## Навіщо це потрібно

Коли люди працюють із великими інструкціями для AI-моделей, майже ніколи не буває так, що перша версія одразу працює ідеально.

Зазвичай процес виглядає інакше.

Спочатку ми пишемо інструкцію. Потім модель виконує її майже правильно, але пропускає якийсь важливий крок. Ми додаємо уточнення. Потім вона перестає пропускати цей крок, але починає помилятися в іншому місці. Ми знову додаємо правило. Потім інструкція стає довшою, складнішою, у ній зʼявляються винятки, повтори, приховані суперечності. Через якийсь час уже важко зрозуміти, де саме потрібно щось виправляти.

У реальній роботі користувач постійно дає зауваження:

```text
ти пропустив self-check;
це треба було питати раніше;
тут не можна було створювати фінальний пакет;
це правило має бути gate, а не рекомендацією;
це треба винести в playbook;
тут потрібен no-op тест;
цей випадок треба запамʼятати для майбутніх задач;
це покращення треба додати в інструкцію, а не просто врахувати один раз.
```

Якщо такі зауваження залишаються тільки в чаті, вони швидко губляться. Модель може врахувати їх у поточній відповіді, але наступна версія playbook-а, library або domain pack-а може не отримати цього покращення.

Тому в Ordo потрібен окремий механізм: не тільки виконувати інструкції, не тільки дебажити їх, не тільки тестувати, а ще й збирати реальний досвід використання та перетворювати його на структуровані записи для покращення.

Цей механізм називається:

```text
Feedback & Improvement Loop
```

---

## Просте пояснення

`Feedback & Improvement Loop` — це контур покращення Ordo-програми.

Його задача — перетворити людське зауваження на структурований запис:

```text
користувач побачив проблему
→ Ordo зафіксувала feedback
→ класифікувала проблему
→ знайшла affected unit
→ запропонувала patch
→ запропонувала тест
→ чекала human approval
→ після підтвердження зміна потрапила в playbook/library/domain pack/compiler
→ regression suite перевірила, що нічого не зламалось
```

Це дуже важлива відмінність від звичайного prompt-підходу.

У prompt-підході зауваження часто виглядає так:

```text
Добре, врахуй це надалі.
```

Але що саме врахувати? Де саме? У якому файлі? У якому правилі? Чи це новий gate? Чи новий тест? Чи уточнення до FREEFORM? Чи зміна domain pack-а? Чи помилка компілятора?

Ordo не має залишати це неясним.

У Ordo feedback має стати артефактом.

![Nebu — ідея: feedback має ставати артефактом](../assets/mascots/64x64/Nebu_idea_64x64.png)

---

## Чим feedback відрізняється від debug і testing

Debug відповідає на питання:

```text
Чому процес пішов саме так?
```

Testing відповідає на питання:

```text
Чи процес працює так, як очікується?
```

Feedback & Improvement Loop відповідає на інше питання:

```text
Що потрібно змінити в Ordo-програмі, щоб вона працювала краще в майбутньому?
```

Ці три частини повʼязані, але не однакові.

Debug може показати, що модель пропустила gate.

Test може показати, що сценарій не пройшов.

Feedback може зафіксувати, що це не випадкова помилка, а проблема в самій інструкції: gate був описаний як рекомендація, але не був визначений як blocking.

---

## Ordo-конструкція

У мові Ordo для цього шару потрібні окремі конструкції.

Базовий набір може виглядати так:

```text
FEEDBACK.CAPTURE
ISSUE.RECORD
IMPROVEMENT.RECORD
PROBLEM.CLASSIFY
ROOT_CAUSE.LINK
AFFECTED.UNIT
PATCH.SUGGEST
TEST.SUGGEST
REGRESSION.ADD
VERSION.NOTE
CHANGELOG.UPDATE
LESSON.LEARNED
```

Їх не потрібно сприймати як фінальний синтаксис. Важлива сама ідея: feedback має бути не текстовою приміткою, а частиною виконуваної системи розвитку Ordo-програми.

---

## Що таке improvement record

`Improvement record` — це структурований запис про проблему або покращення.

Він має містити не тільки текст зауваження, а й контекст:

```text
- хто або що виявило проблему;
- у якому run це сталося;
- який path був активний;
- який node або gate був повʼязаний із проблемою;
- який тип проблеми;
- наскільки вона критична;
- яку частину Ordo-програми треба змінити;
- який patch пропонується;
- який тест потрібно додати;
- чи потрібне human approval;
- чи внесено зміну в changelog.
```

Приклад:

```yaml
improvement_record:
  id: "IR-2026-07-05-001"

  source:
    type: "user_feedback"
    message: "Ти знову пропустив self-check перед архівом."

  classification:
    type: "missed_required_gate"
    severity: "high"

  affected_unit:
    kind: "gate"
    id: "G_PACKAGE_SELF_CHECK"
    owner:
      layer: "domain_pack"
      name: "history_event"

  observed_in:
    run_id: "RUN-2026-07-05-001"
    path: "package_generation"
    node: "final_archive"

  root_cause_hypothesis:
    - "gate exists in documentation but is not enforced as blocking"
    - "archive generation was allowed before validation report"

  proposed_patch:
    - "mark G_PACKAGE_SELF_CHECK as blocking"
    - "add ASSERT.NOT final_archive_created before self_check_passed"

  suggested_tests:
    - id: "TC_NO_ARCHIVE_WITHOUT_SELF_CHECK"
      expected:
        final_archive_created: false
        blocked_gate: "G_PACKAGE_SELF_CHECK"

  approval:
    required: true
    status: "pending"
```

Цей запис уже можна використовувати як основу для реальної зміни в playbook-у.

---

## Affected unit

Один із найважливіших елементів improvement loop — це `affected_unit`.

Користувач може сказати:

```text
Тут щось не так.
```

Але для розвитку Ordo цього недостатньо. Потрібно зрозуміти, де саме проблема.

Проблема може бути в:

```text
- конкретному NODE;
- конкретному GATE;
- статусі;
- ASSERT.NOT;
- output contract;
- FREEFORM-блоці;
- library;
- domain pack;
- profile;
- compiler rule;
- documentation runtime;
- rendered artifact validation;
- test fixture;
- самій структурі playbook-а.
```

Тому improvement record має завжди намагатися привʼязати проблему до конкретної одиниці.

Приклад:

```yaml
affected_unit:
  kind: "library"
  id: "ordo.validation.contract_first"
  version: "0.1"
  export: "G_CONTRACT_CONFIRMED"
```

Або:

```yaml
affected_unit:
  kind: "freeform"
  id: "FF_DOMAIN_EDGE_CASES"
  owner:
    layer: "domain_pack"
    name: "history_event"
```

Це дозволяє не просто виправити один сценарій, а покращити правильне місце.

---

## Класифікація проблем

Feedback потрібно класифікувати.

Інакше всі зауваження перетворяться на хаотичний список.

Типові класи проблем:

```text
missed_required_gate
wrong_path_selected
premature_output
missing_question
wrong_question_order
state_not_updated
state_updated_without_confirmation
implicit_assumption
freeform_overuse
conflicting_rules
library_conflict
missing_test
missing_noop_test
missing_coverage
rendered_artifact_not_validated
compiler_mapping_error
unclear_status_semantics
```

Класифікація допомагає зрозуміти, що саме потрібно зробити.

Наприклад, якщо проблема `missing_question`, можливо, потрібно змінити `NODE.DEF`.

Якщо проблема `premature_output`, можливо, потрібен blocking gate або `ASSERT.NOT`.

Якщо проблема `freeform_overuse`, можливо, частину FREEFORM треба формалізувати.

Якщо проблема `missing_noop_test`, потрібно додати test case.

---

## Human approval

`Feedback loop` не має автоматично переписувати Ordo-програму.

Це дуже важливе правило.

![Nebu — увага: feedback не застосовується без підтвердження](../assets/mascots/64x64/Nebu_attention_64x64.png)

Ordo може:

```text
- зафіксувати проблему;
- запропонувати root cause;
- запропонувати patch;
- запропонувати regression test;
- показати affected unit;
- підготувати changelog note.
```

Але застосування зміни має бути керованим.

Правильний цикл:

```text
feedback captured
→ problem classified
→ affected unit linked
→ patch suggested
→ test suggested
→ human approval required
→ change applied
→ regression suite executed
→ version note / changelog updated
```

Без підтвердження зміна має залишатися у статусі:

```text
pending_improvement
```

Це захищає Ordo від хаотичного самонавчання.

---

## Звʼязок із regression suite

Кожне серйозне зауваження має завершуватися не тільки `patch`-ем, а й тестом.

Погано:

```text
Ми додали в інструкцію: не пропускати self-check.
```

Краще:

```text
Ми додали blocking gate G_PACKAGE_SELF_CHECK.
```

Ще краще:

```text
Ми додали blocking gate G_PACKAGE_SELF_CHECK
і regression test TC_NO_ARCHIVE_WITHOUT_SELF_CHECK.
```

Інакше та сама проблема може повернутися через кілька змін.

Тому Ordo має мати правило:

```text
Кожен high-severity improvement record має пропонувати принаймні один regression test.
```

---

## Звʼязок із changelog

Якщо feedback призвів до зміни Ordo-програми, це має бути відображено в changelog або version note.

Наприклад:

```yaml
version_note:
  version: "0.11.1"
  changes:
    - type: "gate_enforcement"
      description: "G_PACKAGE_SELF_CHECK is now blocking before final archive generation."
      source_improvement_record: "IR-2026-07-05-001"
      regression_tests_added:
        - "TC_NO_ARCHIVE_WITHOUT_SELF_CHECK"
```

Це дозволяє бачити, чому зʼявилась конкретна зміна.

Без цього playbook поступово перетворюється на набір правил, історія появи яких уже нікому не зрозуміла.

---

## Звʼязок із бібліотеками

Коли Ordo отримає механізм libraries, feedback loop має працювати і з ними.

Проблема може виникнути не в основному playbook-у, а в підключеній бібліотеці.

Наприклад:

```yaml
include:
  - library: "ordo.validation.contract_first"
    version: "0.1"
    as: "contract_first"
```

Якщо gate із цієї бібліотеки працює неправильно або не покриває потрібний випадок, improvement record має вказати саме бібліотеку:

```yaml
affected_unit:
  kind: "library"
  id: "ordo.validation.contract_first"
  version: "0.1"
  export: "G_CONTRACT_CONFIRMED"
```

Тоді покращення можна внести не тільки в один playbook, а в reusable рішення, яке потім використають інші Ordo-програми.

---

## Звʼязок із FREEFORM

FREEFORM часто буде джерелом складних проблем.

Це нормально. FREEFORM потрібен саме тому, що не все можна формалізувати одразу.

Але якщо певний FREEFORM-блок постійно викликає помилки, Ordo має це бачити.

Наприклад:

```yaml
freeform_feedback:
  freeform_id: "FF_DOMAIN_EDGE_CASES"
  records:
    - "IR-2026-07-05-004"
    - "IR-2026-07-05-009"
  suggested_action:
    - "split freeform block"
    - "formalize recurring rule as GATE.DEF"
    - "add example-based tests"
```

Тобто feedback loop допомагає поступово зменшувати неконтрольовану частину інструкції.

![Nebu — подумати: повторюваний feedback може показати, що FREEFORM треба формалізувати](../assets/mascots/64x64/Nebu_thinking_64x64.png)

Не обовʼязково прибирати FREEFORM повністю. Але потрібно бачити, де він стає ризиком.

---

## Типові помилки

### 1. Просто сказати “врахуй надалі”

Це слабкий варіант.

У Ordo потрібно не тільки врахувати, а й зафіксувати:

```text
що саме;
де саме;
чому;
який patch;
який тест;
який статус.
```

### 2. Вносити зміни без regression test

Це швидко створює нові проблеми.

Кожне серйозне виправлення має породжувати тест.

### 3. Не привʼязувати проблему до affected unit

Якщо немає affected unit, то незрозуміло, що саме треба змінювати.

### 4. Автоматично застосовувати всі зауваження

Feedback не завжди означає правильну зміну. Іноді користувач описує симптом, але root cause інший.

Тому потрібне human approval.

### 5. Змішувати feedback із debug log

Debug log показує, що сталося.

Feedback record показує, що з цим треба зробити.

---

## Міні-вправа

Візьміть одне реальне зауваження до будь-якої інструкції.

Наприклад:

```text
Модель занадто рано сформувала фінальний документ.
```

Спробуйте оформити його як improvement record:

```text
1. Який тип проблеми?
2. Який severity?
3. Який affected unit?
4. Який root cause?
5. Який patch потрібен?
6. Який regression test потрібно додати?
7. Чи потрібне human approval?
8. Який changelog note треба створити?
```

Після цього стане видно, що feedback — це не просто коментар. Це вхід у процес розвитку Ordo-програми.

---

## Короткий підсумок

`Feedback & Improvement Loop` потрібен, щоб реальний досвід роботи з Ordo не губився.

Він перетворює зауваження користувача на структуровані записи для покращення:

```text
feedback → issue → affected unit → root cause → patch → test → approval → regression → changelog
```

Цей шар робить Ordo мовою не тільки виконання, а й керованого розвитку інструкцій.

Без feedback loop складні playbook-и поступово стають хаотичними.

З feedback loop кожна проблема може стати джерелом контрольованого покращення.

<!-- REVIEWED: chapter 18; Nebu markers checked -->
