# Розділ 56. Session-trace як proof program

`session-trace` — це не опис дерева рішень. Це запис фактичного проходження runtime-сесії.

Ідея: кожне рішення користувача стає не просто полем у state, а рядком у proof program, який можна перевірити.

## Файл trace

Runtime-пакет містить:

```text
runtime/session.ordo.trace
```

На початку trace ініціалізований, але ще не містить user decisions. Кожен accepted `intake --submit` дописує новий step.

## Приклад trace-фрагмента

```ordo-trace
step 001:
  accept N_EVENT_GOAL with answer "Fall of Constantinople" -> N_PATH_SELECT
  evidence sha256:...
  snapshot sha256:...
```

Trace пише CLI. Модель не має права створювати, редагувати або “підправляти” його вручну.

## Як trace повʼязаний із evidence

Після кожного submit CLI оновлює:

```text
reports/intake_submit_report.json
runtime/evidence/*_evidence.json
runtime/state_snapshots/SESSION-*.json
runtime/session.ordo.trace
runtime/live_session_state.json
```

Evidence report містить trace metadata: path, digest, step і fragment. Це дозволяє моделі показати користувачу доказ, не читаючи внутрішні compiled targets напряму.

## Чому trace не замінює snapshot

Snapshot показує стан. Trace показує шлях, яким до цього стану прийшли.

```text
snapshot = що зараз відомо
trace = які рішення привели сюди
```

Тому вони перевіряються разом.

## Перевірка

Команда:

```bash
cli_embedded/ordo verify-session .
```

перевіряє:

```text
target-set
session-chain
session-trace
canary-scan
```

Чиста сесія має показати:

```text
target-set: consistent
session-chain: intact
session-trace: intact
canary-scan: clean
```

Якщо trace змінено вручну, `verify-session` має показати failure. Якщо модель обійшла CLI і не створила trace/evidence, це також стає видимим.

## Навіщо це моделі

Модель у довгій сесії може забути, що саме було підтверджено. Trace зменшує ризик такого дрейфу:

```text
кожен крок має node;
кожен answer має evidence;
кожен перехід має next node;
кожен digest можна перевірити;
усю сесію можна replay/verify логічно.
```

Тобто session-trace робить runtime не просто діалогом, а перевірюваною історією виконання.
