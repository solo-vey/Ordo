# Розділ 57. Scenario testing і PathWalk

У попередніх розділах ми додали до Ordo runtime-пакета кілька шарів перевірки:

```text
CLI-enforced runtime
per-node evidence
hash-chain snapshots
verify-session
multi-target compilation
Ordo-code runtime view
session-trace proof program
```

Це відповідає на питання:

```text
Чи конкретний runtime-прохід має докази і чи можна його перевірити?
```

Але є інше питання:

```text
Чи модель стабільно поводиться правильно у багатьох різних сценаріях?
```

Для цього потрібен окремий testing layer. Один із можливих підходів — **PathWalk**.

## Що таке scenario testing

Звичайний unit-тест CLI перевіряє команду:

```text
next-step працює
intake --submit приймає правильну відповідь
verify-session ловить пошкодження trace
```

Scenario testing перевіряє вже не команду, а поведінку моделі в цілому:

```text
модель отримала runtime package
модель повинна викликати next-step
модель ставить питання користувачу
користувач або тестовий сценарій дає відповідь
модель submit-ить відповідь через CLI
CLI пише evidence, snapshot і trace
модель переходить далі тільки після прийнятого submit
```

Тобто scenario testing відповідає на практичне питання:

```text
Чи модель реально йде по Process Rail, а не просто каже, що йде?
```

## Що таке PathWalk

PathWalk — це супровідна утиліта або benchmark-підхід для перевірки проходження Ordo-сценаріїв.

Вона може:

```text
створювати тестове дерево рішень
генерувати ground truth path
давати моделі пройти цей шлях
додавати шум, уточнення або неправильні відповіді
перевіряти фактичні runtime-артефакти після проходу
рахувати score
```

PathWalk не є частиною ядра Ordo. Це зовнішній або companion-шар.

Його задача — не замінити runtime CLI, а перевірити, чи модель ним користується.

## Чому не можна вірити самозвіту моделі

Модель може написати:

```text
CLI executed and passed.
```

Але це саме по собі нічого не доводить.

Після M59/M60 доказами є файли:

```text
reports/next_step_report.json
reports/intake_submit_report.json
runtime/evidence/*_evidence.json
runtime/state_snapshots/*.json
runtime/session.ordo.trace
reports/target_verification_report.json
reports/session_verification_report.json
```

PathWalk має дивитися саме на ці файли.

Інакше ми знову повертаємось до старої проблеми:

```text
модель сама сказала, що все пройшла правильно
але ніхто не перевірив, що CLI справді викликався
```

## Як PathWalk має працювати з M60 runtime package

У enforced mode PathWalk має давати моделі тільки runtime CLI-протокол.

Типовий цикл:

```bash
./cli_embedded/ordo runtime-status .
./cli_embedded/ordo verify-targets .
./cli_embedded/ordo next-step . --format auto
./cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <answer-file>
./cli_embedded/ordo verify-session .
```

Модель не має читати напряму:

```text
compiled/program.ir.json
compiled/program.ordo.view
compiled/targets.manifest.json
```

Навіть `program.ordo.view` є AI-facing projection, але вона має подаватися через CLI, а не через пряме читання файла.

## Як PathWalk повʼязаний із трьома M60 target-ами

У M60 є проста формула:

```text
JSON IR вирішує.
Ordo-code пояснює.
Session-trace доводить.
```

PathWalk має використовувати її так:

```text
JSON IR
  не читається моделлю напряму, але є canonical runtime contract для CLI.

Ordo-code view
  може бути показаний моделі через next-step --format auto або render-runtime-view.

Session-trace
  перевіряється після проходу як proof program фактичних прийнятих рішень.
```

Тобто PathWalk не створює нове джерело правди. Він перевіряє, чи модель коректно працює з уже наявними джерелами доказу.

## Режими, які варто порівнювати

PathWalk особливо корисний, якщо порівнювати кілька режимів:

```text
enforced + json
enforced + ordo-code
enforced + json,ordo-code
ir_readable baseline
freeform baseline
```

Наприклад, можна перевірити:

```text
чи модель частіше помиляється у json-only режимі
чи Ordo-code view допомагає їй краще тримати allowed answers
чи mixed режим дає кращу стабільність
чи freeform режим швидше дрейфує від дерева рішень
```

Це вже не просто тест Ordo. Це вимірювання поведінки моделі.

## Що PathWalk має оцінювати

Один загальний score недостатній. Краще розділяти оцінку:

```text
path correctness
  чи фінальний шлях збігся з очікуваним

protocol compliance
  чи модель кожного разу викликала CLI

runtime integrity
  чи verify-targets і verify-session пройшли

compiled-read violations
  чи модель намагалася читати compiled/* напряму

robustness
  чи модель витримала уточнення, шум, неправильні відповіді або корекції
```

Це важливо, бо модель може прийти до правильного фінального вузла, але зробити це неправильним способом.

Для Ordo правильний спосіб теж має значення.

## Backtracking і restore-session

У guided intake реальні користувачі часто змінюють думку:

```text
ні, повернімось назад
я помилився у попередній відповіді
обери іншу гілку
```

Це природний сценарій. Але станом на M60.3 `restore-session` ще не є обовʼязковою runtime-командою.

Тому PathWalk може тестувати прості корекції, якщо вони підтримані самим деревом. Але повноцінний rollback краще робити окремим майбутнім шаром:

```text
restore-session має бути append-only
має писати evidence
має писати trace event
має перевірятися verify-session
не має мовчки видаляти історію
```

Тобто backtracking важливий, але його не треба робити хаотичним ручним редагуванням state.

## Чого PathWalk не повинен робити

PathWalk не має:

```text
підміняти embedded CLI
самостійно створювати evidence reports від імені CLI
пропонувати моделі читати compiled/*
рахувати успіх тільки за текстом відповіді моделі
вважати protocol bypass нормальним, якщо фінальний answer виглядає правильним
```

Якщо тестова утиліта робить це, вона може бути корисною для baseline, але не для enforced-runtime перевірки.

## Підсумок

Runtime CLI перевіряє один конкретний прохід.

PathWalk перевіряє, чи модель стабільно проходить багато різних сценаріїв.

У правильній архітектурі вони не конкурують:

```text
Ordo runtime package дає правила і докази.
PathWalk дає експеримент над поведінкою моделі.
```

Саме тому PathWalk варто документувати як окремий companion testing layer, а не як частину ядра мови.


## M60.3.2: чому bare intake заборонений у benchmark-автоматизації

Scenario runner не повинен викликати CLI так:

```bash
./cli_embedded/ordo intake .
```

Такий виклик означає: “запусти guided intake і, якщо відповіді немає, запитай через `input()`”. Для людини в терміналі це нормально. Для subprocess/benchmark worker — небезпечно, бо процес може зависнути.

Починаючи з M60.3.2, Ordo runtime CLI має поводитися так:

```text
немає --submit
немає --answers
немає --non-interactive
stdin не є TTY
        ↓
fail-fast
reason: no_answers_and_not_interactive_and_no_tty
```

Для PathWalk це означає просте правило:

```text
у benchmark automation завжди використовуй явний режим:
- intake --submit ...
- або intake --answers ... --non-interactive
```

Так само `next-step` має давати моделі короткий поточний фрагмент, а не весь внутрішній checkpoint table. Повні деталі можуть існувати у report-файлі, але модель не повинна отримувати зайвий runtime шум у stdout.
