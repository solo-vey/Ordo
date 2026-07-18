# Розділ 58. Restore-session: безпечне повернення назад

Іноді під час guided intake користувач хоче змінити попередню відповідь:

```text
Повернімось на попередній крок.
Я хочу обрати інший шлях.
Ні, ця відповідь була помилкова.
```

До M60.4 у runtime Ordo не було нативної команди для такого повернення. Це створювало спокусу для зовнішніх утиліт або моделі самостійно редагувати стан сесії. Такий підхід небезпечний: він може приховати, що історію було змінено.

M60.4 додає команду:

```bash
ordo restore-session <package> --to-seq <N>
```

У runtime-пакеті вона викликається так:

```bash
./cli_embedded/ordo restore-session . --to-seq <N>
```

## Restore — це не видалення історії

Головне правило:

```text
restore-session не стирає минулі snapshots.
restore-session додає нову подію в історію.
```

Тобто Ordo не “перемотує” сесію так, наче пізніших кроків ніколи не було. Замість цього CLI бере стан із попереднього snapshot і створює нову restore-подію.

Це важливо для довіри: людина й перевіряюча утиліта бачать, що відбулося повернення.

## Що пише restore-session

Успішний restore створює або оновлює:

```text
reports/restore_session_report.json
runtime/evidence/*RESTORE_TO_SEQ_<N>*_evidence.json
runtime/state_snapshots/SESSION-*_RESTORE_TO_SEQ_<N>.json
runtime/session.ordo.trace
runtime/live_session_state.json
```

У `session.ordo.trace` зʼявляється крок:

```text
action: restore_session
node: RESTORE_TO_SEQ_<N>
```

Це означає: повернення назад є частиною доказової історії, а не прихованою операцією над файлами.

## Як модель має працювати після restore

Після restore модель не повинна самостійно вирішувати, яке питання ставити далі. Вона має знову викликати CLI:

```bash
./cli_embedded/ordo next-step . --format auto
```

Тільки після цього вона може поставити користувачу наступне питання.

## Як перевірити restore

Фінальна перевірка та сама:

```bash
./cli_embedded/ordo verify-session .
```

Сесія вважається здоровою, якщо restore-подія не ламає:

```text
target-set
session-chain
session-trace
evidence digest
snapshot hash
canary scan
```

## Чому це важливо для PathWalk

Scenario-testing утиліти на кшталт PathWalk часто мають correction/backtrack сценарії. До M60.4 вони могли або не тестувати такі сценарії, або мати власний rollback-механізм.

Після M60.4 правильний підхід інший:

```text
PathWalk не має сам переписувати runtime state.
PathWalk має викликати embedded CLI restore-session.
```

Так зберігається головна властивість Ordo runtime: кожен важливий перехід видно в доказових артефактах.

## Формула M60.4

```text
JSON IR вирішує.
Ordo-code пояснює.
Session-trace доводить.
Restore-session повертає назад без стирання історії.
```
