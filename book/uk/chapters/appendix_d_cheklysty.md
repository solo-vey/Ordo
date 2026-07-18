# Додаток D. Чеклисти

Цей додаток містить практичні чеклисти для роботи з Ordo-програмами. Їх можна використовувати під час створення нового playbook-а, ревізії існуючої інструкції, підготовки domain pack-а, підключення бібліотек, дебагу, тестування або фінальної перевірки перед передачею в роботу.

Чеклист в Ordo — це не заміна gates і не заміна тестів. Це допоміжний інструмент для автора, аналітика або reviewer-а, який допомагає не пропустити важливі частини процесу.

## D.1. Чеклист готовності ідеї до Ordo

Перед тим як перетворювати інструкцію на Ordo-програму, потрібно зрозуміти, чи є в ній керований процес.

```text
[ ] Є зрозумілий intent.
[ ] Є очікуваний результат.
[ ] Є межі відповідальності моделі.
[ ] Є речі, які модель не має робити.
[ ] Є точки, де потрібне підтвердження людини.
[ ] Є варіанти шляху виконання.
[ ] Є дані, які потрібно зібрати перед дією.
[ ] Є правила, які не можна пропускати.
[ ] Є фінальний handoff або output.
[ ] Є ризик помилки, який виправдовує формалізацію.
```

Якщо більшість пунктів порожні, можливо, це ще не Ordo-програма, а звичайне коротке прохання до моделі.

Якщо більшість пунктів заповнені, це хороший кандидат для Ordo.

## D.2. Чеклист Intent

Intent має відповідати на питання: що користувач насправді хоче отримати?

```text
[ ] Intent сформульований одним або кількома простими реченнями.
[ ] Intent не змішаний з implementation details.
[ ] Intent не містить непідтверджених припущень.
[ ] Intent відділений від output format.
[ ] Intent не підміняється назвою задачі.
[ ] Intent не описує випадковий приклад замість загальної мети.
[ ] Intent зрозумілий людині без читання всієї програми.
```

Поганий intent:

```text
Зробити як у попередньому прикладі.
```

Кращий intent:

```text
Провести користувача через керований збір даних для створення аналітичного пакета історичної події.
```

## D.3. Чеклист Contract

Contract визначає, що саме має бути підтверджено до початку або до критичних дій.

```text
[ ] Відомо, які поля обов’язкові.
[ ] Відомо, які рішення має підтвердити користувач.
[ ] Відомо, що можна вважати confirmed.
[ ] Відомо, що не можна вважати confirmed.
[ ] Є правила для неповного contract.
[ ] Є gate, який блокує подальше виконання без contract.
[ ] Contract не формується мовчки з припущень моделі.
[ ] Contract зберігається у state.
[ ] Зміни contract фіксуються як state diff.
```

Критичне правило:

```text
Якщо contract не підтверджений, модель не має поводитися так, ніби він підтверджений.
```

## D.4. Чеклист Context

Context — це дані, документи, правила, приклади й обмеження, які потрібні для правильного виконання.

```text
[ ] Вказано, які документи є джерелами правил.
[ ] Вказано, які дані є вхідними.
[ ] Вказано, які приклади є лише прикладами.
[ ] Вказано, які частини context мають вищий пріоритет.
[ ] Вказано, що робити при конфлікті джерел.
[ ] Вказано, які дані не можна вигадувати.
[ ] Вказано, які джерела можна цитувати або використовувати як evidence.
[ ] Context не змішаний із state.
```

## D.5. Чеклист State

State показує, що вже відомо, що підтверджено, що очікує рішення і що заборонено.

```text
[ ] State має явну схему.
[ ] State містить confirmed і pending значення.
[ ] State не змішує факт і припущення.
[ ] State оновлюється після кожного важливого кроку.
[ ] Є state snapshot для debug mode.
[ ] Є state diff для зміни значень.
[ ] Не використовується прихована пам’ять замість state.
[ ] Критичні рішення не губляться в тексті відповіді.
```

Приклад корисного state:

```yaml
state:
  contract:
    alias:
      value: "LU_CHANGE_STATUS"
      status: "confirmed"

  approvals:
    pre_archive:
      status: "pending"

  execution:
    selected_path: "A1"
```

## D.6. Чеклист Entry і Node

Entry і Node відповідають за керований діалог.

```text
[ ] Є стартовий ENTRY.
[ ] Кожен NODE має зрозумілу мету.
[ ] Кожен NODE ставить тільки потрібні питання.
[ ] NODE не забігає наперед.
[ ] NODE має умови входу.
[ ] NODE має умови виходу.
[ ] NODE оновлює state.
[ ] NODE знає, куди перейти далі.
[ ] Є правила для невизначеної відповіді користувача.
[ ] Є правила для зміни попереднього рішення.
```

Погано:

```text
Спитай у користувача все, що потрібно.
```

Краще:

```yaml
node:
  id: "N_COLLECT_ALIAS"
  asks:
    - "Підтверди alias події."
  writes:
    - "state.contract.alias"
  next:
    when_confirmed: "N_COLLECT_SOURCE_FIELD"
```

## D.7. Чеклист Path

Path потрібен там, де один і той самий intent може виконуватися різними шляхами.

```text
[ ] Усі основні paths перелічені.
[ ] Для кожного path є умови вибору.
[ ] Для кожного path є reason.
[ ] Є список rejected paths у debug mode.
[ ] Є правило, що робити при неоднозначності.
[ ] Є gate або user approval для ризикового path.
[ ] Path не обирається за інтуїцією моделі.
[ ] Path selection можна протестувати.
```

## D.8. Чеклист Gate

Gate — це контрольна точка, а не порада.

```text
[ ] Gate має id.
[ ] Gate має умову проходження.
[ ] Gate має статус.
[ ] Gate має evidence.
[ ] Gate має наслідок при fail/block.
[ ] Відомо, чи gate blocking.
[ ] Gate не можна пройти без потрібних даних.
[ ] Gate не ховається у FREEFORM.
[ ] Gate відображається у debug trace.
[ ] Gate має тест або coverage.
```

Критичне правило:

```text
Якщо gate є blocking, модель не має права продовжити дію, яку gate блокує.
```

## D.9. Чеклист ASSERT.NOT

Негативні перевірки потрібні, щоб заборонити небезпечні дії.

```text
[ ] Є список дій, які модель не має робити.
[ ] Для кожної забороненої дії є ASSERT.NOT.
[ ] ASSERT.NOT прив’язаний до конкретного ризику.
[ ] ASSERT.NOT перевіряється перед output.
[ ] ASSERT.NOT має тест.
[ ] ASSERT.NOT не замінений м’якою рекомендацією.
```

Приклади:

```text
[ ] Не створювати фінальний архів до approval.
[ ] Не вигадувати source row.
[ ] Не трактувати example як confirmed rule.
[ ] Не змінювати contract без підтвердження.
```

## D.10. Чеклист Output

Output має бути явним і перевірюваним.

```text
[ ] Вказано тип output.
[ ] Вказано формат output.
[ ] Вказано обов’язкові частини output.
[ ] Вказано, що не має входити в output.
[ ] Вказано, які gates мають бути пройдені перед output.
[ ] Output можна перевірити через validation.
[ ] Output має handoff note або next action.
[ ] Output не створюється раніше дозволеного моменту.
```

## D.11. Чеклист FREEFORM

FREEFORM потрібен для складних смислових частин, але він має бути контрольованим.

```text
[ ] У FREEFORM є id.
[ ] Є reason, чому ця частина не формалізована.
[ ] Є purpose.
[ ] Є binding.
[ ] Вказано, де FREEFORM використовується.
[ ] Вказано, що FREEFORM не може override.
[ ] Є coverage або план coverage.
[ ] Немає прихованих gates усередині FREEFORM.
[ ] Немає прихованих статусів усередині FREEFORM.
[ ] Немає правил, які краще винести в Core/Profile/Domain Pack.
```

## D.12. Чеклист Debug

Debug mode має пояснювати виконання, а не просто дублювати відповідь.

```text
[ ] Є run_id.
[ ] Є input snapshot.
[ ] Є selected path.
[ ] Є rejected paths with reasons.
[ ] Є decision log.
[ ] Є state snapshots.
[ ] Є state diffs.
[ ] Є gate report.
[ ] Є knowledge trace.
[ ] Є warnings.
[ ] Є violations.
[ ] Є failure explanation, якщо процес зламався.
```

Debug trace має відповідати на питання:

```text
Чому модель зробила саме це?
```

## D.13. Чеклист Test

Тести мають перевіряти поведінку Ordo-програми, а не тільки фінальний текст.

```text
[ ] Є TEST.DEF.
[ ] Є FIXTURE.DEF.
[ ] Є expected path.
[ ] Є expected state.
[ ] Є expected gates.
[ ] Є expected output.
[ ] Є EXPECT.NOT для заборонених дій.
[ ] Є no-op тести.
[ ] Є негативні тести.
[ ] Є тести для edge cases.
[ ] Є тести для FREEFORM-backed рішень.
```

## D.14. Чеклист Regression Suite

Regression suite потрібен перед змінами.

```text
[ ] Є набір базових сценаріїв.
[ ] Є сценарії для кожного path.
[ ] Є сценарії для blocking gates.
[ ] Є сценарії для no-op.
[ ] Є сценарії для помилкових або неповних input.
[ ] Є сценарії для бібліотек.
[ ] Є сценарії для domain pack.
[ ] Regression suite запускається перед release.
[ ] Результат regression suite фіксується в report.
```

## D.15. Чеклист Coverage

Coverage показує, наскільки Ordo-програма справді покрита контролем.

```text
[ ] Покриті всі основні paths.
[ ] Покриті всі blocking gates.
[ ] Покриті всі критичні ASSERT.NOT.
[ ] Покриті всі output types.
[ ] Покриті всі status transitions.
[ ] Покриті no-op сценарії.
[ ] Покриті critical FREEFORM blocks.
[ ] Покриті imported libraries.
[ ] Є список uncovered areas.
[ ] Є план покращення coverage.
```

## D.16. Чеклист Feedback & Improvement Loop

Коли користувач вказує на проблему, її потрібно перетворити на structured record.

```text
[ ] Feedback captured.
[ ] Вказано original user message.
[ ] Проблему класифіковано.
[ ] Вказано severity.
[ ] Вказано affected unit.
[ ] Є root cause hypothesis.
[ ] Є proposed patch.
[ ] Є suggested test.
[ ] Є required approval.
[ ] Є version note або changelog item.
[ ] Є regression test після виправлення.
```

Feedback не має губитися в чаті.

## D.17. Чеклист бібліотек Ordo

Для підключених бібліотек потрібно контролювати версії, namespace і конфлікти.

```text
[ ] Бібліотека підключена явно.
[ ] Версія зафіксована.
[ ] Є alias або namespace.
[ ] Вказано, які exports використовуються.
[ ] Виконано compatibility check.
[ ] Перевірено конфлікти.
[ ] Override дозволений тільки явно.
[ ] Немає implicit imports.
[ ] Є trust level.
[ ] Бібліотека покрита тестами або має власний test pack.
```

Погано:

```yaml
include:
  - "ordo.qa"
```

Краще:

```yaml
include:
  - library: "ordo.qa.manual_runbook"
    version: "0.1"
    as: "manual_qa"
```

## D.18. Чеклист Domain Pack

Domain Pack має описувати доменну логіку, а не випадковий набір прикладів.

```text
[ ] Є domain vocabulary.
[ ] Є domain-specific paths.
[ ] Є domain-specific gates.
[ ] Є domain-specific statuses.
[ ] Є domain-specific output templates.
[ ] Є mapping до Ordo Core.
[ ] Є controlled FREEFORM для складних edge cases.
[ ] Є domain tests.
[ ] Є coverage report.
[ ] Є improvement loop.
```

## D.19. Чеклист міграції старого playbook-а в Ordo

```text
[ ] Старий playbook розбитий на логічні частини.
[ ] Визначено intent.
[ ] Визначено contract.
[ ] Визначено decision tree.
[ ] Визначено paths.
[ ] Визначено nodes.
[ ] Визначено gates.
[ ] Визначено statuses.
[ ] Визначено outputs.
[ ] Визначено handoff.
[ ] Визначено FREEFORM blocks.
[ ] Визначено libraries, які можна підключити.
[ ] Побудовано Semantic JSON IR.
[ ] Створено test cases.
[ ] Створено coverage report.
[ ] Проведено consistency check.
```

## D.20. Чеклист перед фінальним handoff

Перед передачею Ordo-програми або пакета в роботу потрібно перевірити:

```text
[ ] Усі mandatory sections присутні.
[ ] Немає невирішених blocking gates.
[ ] Немає pending contract fields.
[ ] Немає unresolved conflicts.
[ ] Немає implicit assumptions.
[ ] Немає hidden rules у FREEFORM.
[ ] Debug trace можна отримати.
[ ] Regression suite пройдений або чесно вказано, що він ще не створений.
[ ] Coverage report сформований.
[ ] Improvement records враховані або перенесені в backlog.
[ ] Version note оновлений.
[ ] Handoff note написаний.
```

## Короткий підсумок

Чеклисти не роблять Ordo-програму правильною автоматично. Але вони допомагають автору не пропустити ключові речі:

```text
intent
contract
context
state
path
node
gate
assertion
output
debug
test
coverage
feedback
library
domain pack
handoff
```

Якщо Ordo-програма проходить ці чеклисти, її вже можна не тільки читати, а й підтримувати, тестувати, покращувати і передавати іншим людям або системам.

---

## D.22. Чеклист Ordo v0.12 Reliability

Цей чеклист використовується після оновлення програми або playbook-а до Ordo v0.12.

```text
[ ] Кожен gate має обовʼязкове поле method.
[ ] Для кожного gate вказано trust_class.
[ ] Mechanical gates не змішані з semantic model-judgment gates.
[ ] Gates з method: self_verification мають evidence protocol.
[ ] Критичні semantic gates мають generator/critic або self_consistency pattern.
[ ] Gate report показує method і trust_class.
[ ] Execution trace має trace_source.
[ ] Ordo-програма має execution_mode.
[ ] У документації не створено враження, що model_self_report дорівнює runtime_enforced log.
[ ] ASSERT.NOT описаний як shortcut/projection від ASSERTION.
[ ] Критичні заборони оформлені як ASSERTION з phase: [runtime, test].
[ ] EXPECT.NOT не дублює вручну ASSERT.NOT, а походить із ASSERTION projection.
[ ] NODE має on_unmatched_input або явно описаний fallback.
[ ] Для unmatched input передбачено CLARIFY.REQUEST.
[ ] Feedback class node_coverage_gap використовується для повторюваних непокритих відповідей.
[ ] Program має control_level: light / standard / strict.
[ ] Strict-програма має regression coverage для mandatory gates і assertions.
[ ] У trace, gate_report і improvement_record використовуються namespaced IDs.
[ ] Includes мають version.
[ ] Layer priority визначений і не порушений.
[ ] Override є явним і має reason.
[ ] Немає unresolved layer conflicts.
[ ] FREEFORM-блоки мають maturity.
[ ] FREEFORM incident_count і incident_threshold визначені там, де блок ризиковий.
[ ] FREEFORM з перевищеним threshold має formalization warning або improvement record.
```

## D.23. Чеклист gate.method

```text
[ ] method: mechanical використовується тільки для детермінованих перевірок.
[ ] method: self_verification використовується для семантичних суджень моделі з evidence.
[ ] method: self_consistency використовується для критичних повторюваних модельних перевірок.
[ ] method: human використовується для людських рішень.
[ ] У прикладах немає GATE.CHECK без method.
[ ] У gate_report немає status: passed без пояснення method/trust_class.
```

## D.24. Чеклист execution_mode

```text
[ ] full_runtime використовується тільки там, де runner реально контролює переходи.
[ ] chat_internal чесно описаний як проміжний режим.
[ ] freeform_only не подається як повноцінне контрольоване виконання.
[ ] У chat_internal явно описано, що точка запуску gate не примусова без зовнішнього runtime.
[ ] Для chat_internal описано state_backing або інший спосіб зменшити drift state.
[ ] Для strict-процесів freeform_only не використовується без окремого warning.
```

## D.25. Чеклист ASSERTION

```text
[ ] Заборони описані через ASSERTION.
[ ] У кожного ASSERTION є polarity.
[ ] У кожного ASSERTION є phase.
[ ] Blocking assertion має severity: block.
[ ] Runtime projection створює ASSERT.NOT або gate.
[ ] Test projection створює EXPECT.NOT.
[ ] Debug projection створює violation record.
[ ] Regression suite перевіряє критичні assertions.
```

## D.26. Чеклист namespace/version/layer priority

```text
[ ] Source може мати локальні IDs, але IR має повні namespaced IDs.
[ ] Усі improvement records посилаються на namespaced IDs.
[ ] Усі libraries мають version.
[ ] Floating version не використовується для strict-процесів.
[ ] Core не перекривається нижчим шаром без explicit override.
[ ] Domain Pack не мовчки змінює Profile.
[ ] Library не мовчки змінює Domain Pack.
[ ] FREEFORM не може перекрити формальне правило.
[ ] G_NO_UNRESOLVED_LAYER_CONFLICT присутній для складних програм.
```

