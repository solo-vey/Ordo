# Розділ 74. EXECUTION_TRACE — повна історія виконання процесу

`EXECUTION_TRACE` — це повноцінний елемент мови Ordo, який зберігає фактичну історію одного запуску процесу. Це не звичайний лог і не приховані міркування моделі. Це структурований, перевірюваний журнал того, які вузли, шляхи, дії, рішення, gates, зміни стану та outputs реально виникли під час виконання.

Основне правило:

```text
один RUN → один основний EXECUTION_TRACE
```

Trace зберігається як append-only послідовність подій. Уже записана подія не переписується; виправлення або уточнення додається новою подією. Завдяки цьому trace можна використовувати для audit, debug, replay, regression testing, аналізу роботи аналітика та покращення playbook-а.

## Головна структура

```yaml
execution_trace:
  id: trace.history_event.001
  version: "1.0"
  run:
    run_id: run.history_event.001
    process_id: history_event.guided_intake
    process_version: "1.42"
    execution_mode: normal
    runtime_mode: chat_internal
    trace_source: hybrid
  status: running
  started_at: "2026-07-10T14:00:00+03:00"
  actor:
    actor_type: analyst
  source:
    entry_point: start
    input_refs: []
  capture_level: standard
  events: []
  replay:
    replayable: false
    replay_mode: deterministic
    required_inputs_preserved: false
  integrity:
    event_count: 0
    sequence_complete: true
```

## Що фіксує одна подія

Кожна подія має номер послідовності, стабільний ID, тип, час, виконавця, payload і outcome. За потреби вона також посилається на активний node/path/phase, state before/after, decision, gate, output або батьківську подію.

## Рівні деталізації

- `minimal` — lifecycle запуску, path, gates та outputs;
- `standard` — також inputs, decisions і state diffs;
- `full` — також actions, validations, warnings і checkpoints;
- `audit` — повна доказовість, actor attribution та integrity chain.

Стандартне значення — `standard`.

## Replay

Trace може підтримувати чотири режими: `deterministic`, `re_evaluate`, `simulation`, `audit_only`. Прапорець `replayable: true` дозволений лише тоді, коли потрібні inputs збережені або безпечно referenced, а для зовнішніх залежностей визначено strategy.

## Безпека

Trace не зберігає паролі, токени, секрети, повні конфіденційні документи або приватний chain of thought. Для чутливих значень використовуються redaction, secure reference або hash. Для рішень моделі зберігається короткий reason code та evidence references.

## Відмінність від TRACE.LOG

`TRACE.LOG` — окреме діагностичне повідомлення. `EXECUTION_TRACE` — повний canonical artifact усього запуску. Багато `TRACE.LOG` можуть бути частиною одного `EXECUTION_TRACE`, але не замінюють його.

## Legacy-сумісність

Старий блок `trace:` залишається сумісним представленням. Нові Ordo-програми повинні використовувати `execution_trace:`. Старі поля перетворюються адаптером на canonical trace events.


## Як компілятор і runtime працюють з EXECUTION_TRACE

Компілятор не записує історію виконання. Він перетворює блок `execution_trace:` на нормалізовану інструкцію `EXECUTION_TRACE.DEF`: чи увімкнений trace, який рівень деталізації використати, куди записувати файл і який replay-режим дозволений.

Runtime перед першим кроком створює `runtime/execution_trace.json`, після кожної змістовної дії додає незмінну подію, а при завершенні додає terminal event, фінальний стан і checksum. Після terminal status нові події додавати заборонено.

Рівень `minimal` зберігає лише каркас проходження; `standard` додає відповіді, рішення і зміни стану; `full` — технічні дії та попередження; `audit` — усі дозволені типи подій. Формат файла в усіх випадках однаковий.

Replay може бути детермінованим, із повторним обчисленням правил, симуляційним без side effects або лише аудиторським. Секрети автоматично редагуються, а внутрішній chain-of-thought моделі не потрапляє у trace.
