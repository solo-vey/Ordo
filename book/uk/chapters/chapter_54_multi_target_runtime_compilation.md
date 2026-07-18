# Розділ 54. Multi-target Runtime Compilation Layer

M60 додає до Ordo горизонтальну модель compilation targets. Ідея проста: Ordo не замінює JSON на інший формат, а генерує кілька похідних представлень із одного canonical model.

```text
source/program.ordo.yaml
        ↓
canonical normalized model
        ↓
target emitters
        ├─ compiled/program.ir.json
        ├─ compiled/program.ordo.view
        └─ runtime/session.ordo.trace
```

## Чому не замінити JSON

Semantic JSON IR добре працює як machine contract:

```text
стабільний
hashable
machine-readable
зручний для CLI
зручний для verify-session
```

Але для моделі JSON часто виглядає як “дані”, які можна трошки переставити або доповнити. Тому Ordo додає AI-facing projection, яка виглядає як code-like контракт, але не стає другим source of truth.

## Три перші targets

M60 бере тільки три формати:

```text
json-ir
ordo-code-view
session-trace
```

Python і Java targets не входять у цей етап.

## Головна формула M60

```text
JSON IR decides.
Ordo-code explains.
Session-trace proves.
```

Українською:

```text
JSON IR вирішує.
Ordo-code пояснює.
Session-trace доводить.
```

## `json-ir`

`compiled/program.ir.json` лишається canonical runtime target. CLI виконує runtime logic саме з нього.

Runtime-пакет ніколи не створюється без `json-ir`, навіть якщо обрано `--runtime-view ordo-code`.

## `ordo-code-view`

`compiled/program.ordo.view` — code-like projection для моделі. Вона показує node contract у формі, де явно видно:

```text
kind
question
allowed answers
transition
reject rules
evidence requirements
```

Але модель не читає цей файл напряму. Вона отримує фрагменти через CLI:

```bash
ordo next-step . --format ordo-code
ordo render-runtime-view . --format ordo-code --node <NODE_ID>
```

## `session-trace`

`runtime/session.ordo.trace` — це append-only proof program. Його пише CLI під час реального проходження intake. Модель не має права писати або ремонтувати trace сама.

## Target manifest

Щоб targets не дрейфували один від одного, M60 додає:

```text
compiled/targets.manifest.json
```

У ньому записано:

```text
canonical_ir_hash
target paths
target roles
target hashes
derived_from_ir_hash
mutable session-trace metadata
```

Команда:

```bash
ordo verify-targets .
```

має показати:

```text
target-set: consistent
```

## Головна небезпека

Multi-target система небезпечна, якщо кожен target починає жити окремим життям.

Тому правило жорстке:

```text
один canonical IR;
усі інші targets — похідні;
усі targets перевіряються hash-ами;
Runtime Mode працює тільки через CLI.
```
