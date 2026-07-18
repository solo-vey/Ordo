# Розділ 49. Runtime Guided Intake Entry Protocol

Runtime Guided Intake Entry Protocol — це правило, яке не дає моделі починати guided intake “з памʼяті” або з вільного читання файлів.

У ранніх версіях runtime стартував через `START_HERE_RUNTIME_MODE.md`, `ordo.yml` і compiled IR. Після M59/M60 enforced Runtime Mode став жорсткішим: у runtime-пакеті source YAML не потрібен, а `compiled/*` файли не читаються моделлю напряму.

## Поточний маршрут

```text
START_HERE_RUNTIME_MODE.md
→ cli_embedded/ordo runtime-entry .
→ cli_embedded/ordo next-step . --format auto
→ user answer
→ cli_embedded/ordo intake . --submit <NODE_ID> --answer-file <answer_file>
→ evidence + snapshot + session-trace
→ next CLI-rendered step
```

Це означає: модель не вирішує сама, який node наступний. Вона отримує наступний крок із CLI.

## Чому не можна читати compiled IR напряму

`compiled/program.ir.json` є canonical machine target. Але в Runtime Mode він належить CLI, а не моделі.

Модель не повинна:

```text
відкривати compiled/program.ir.json;
читати compiled/program.ordo.view напряму;
формувати питання з compiled/*;
цитувати compiled/* у чат.
```

Легальні джерела — тільки CLI-команди:

```text
runtime-entry
next-step
next-step --format auto
next-step --format ordo-code
render-runtime-view
intake --submit
verify-targets
verify-session
```

## Короткий протокол після відповіді

Після кожної відповіді користувача AI має показати короткий runtime-протокол:

```text
Крок: <submitted node>
Дія: intake --submit
Результат: accepted / rejected / blocked
Evidence: <path> sha256=<digest>
Trace: runtime/session.ordo.trace sha256=<digest>
Рішення: ask next / clarify / stop
```

Без evidence і trace digest не можна ставити наступне питання.

## Runtime view

M60.3 додає `runtime_view`:

```text
json
ordo-code
json,ordo-code
```

У `json` mode AI бачить стандартний report. У `ordo-code` mode `next-step --format auto` додає current contract fragment. У mixed mode дозволені обидва формати.

## Головна формула

```text
JSON IR вирішує.
Ordo-code пояснює.
Session-trace доводить.
```

Цей протокол не замінює `validate-state`, `validate-output`, `validate-artifacts`, `consistency`, `go-no-go` або `verify-session`. Він задає правильний старт і правильний цикл guided intake.
