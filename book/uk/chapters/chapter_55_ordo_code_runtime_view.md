# Розділ 55. Ordo-code Runtime View

`ordo-code-view` — це AI-facing projection, яка показує runtime contract у вигляді code-like фрагмента. Вона створена не для людини-розробника, а для того, щоб модель бачила процес як строгий контракт, а не як вільний JSON.

## Приклад

Замість того щоб модель бачила сирий JSON, CLI може повернути:

```ordo
node N_PATH_SELECT {
  kind: branch
  answer_type: enum

  allowed {
    A -> N_EVENT_ALIAS
    B -> N_EVENT_ALIAS
    C -> N_EVENT_ALIAS
    D -> N_EVENT_ALIAS
  }

  reject unless answer in [A, B, C, D]

  evidence required:
    next_step_report
    intake_submit_report
    runtime_evidence
}
```

Такий фрагмент моделі важче “вільно інтерпретувати”: тут видно, що дозволені тільки A/B/C/D, що інша відповідь має бути rejected, і що без evidence не можна рухатися далі.

## Чому це не Java і не Python

Ordo-code навмисно не є general-purpose мовою. У ньому немає imports, loops, side effects або довільної логіки.

Його задача — бути:

```text
code-like
strict
читабельним для моделі
обмеженим Ordo state machine
похідним від JSON IR
```

## Як модель має його отримувати

Легально:

```bash
cli_embedded/ordo next-step . --format auto
cli_embedded/ordo next-step . --format ordo-code
cli_embedded/ordo render-runtime-view . --format ordo-code --node <NODE_ID>
```

Нелегально:

```text
відкрити compiled/program.ordo.view напряму
прочитати compiled/program.ir.json напряму
переказати compiled/* у чат
```

У Runtime Mode усі `compiled/*` файли належать CLI.

## Runtime view modes

M60.3 дозволяє створити runtime package у трьох режимах:

```bash
ordo package . --profile runtime --runtime-view json
ordo package . --profile runtime --runtime-view ordo-code
ordo package . --profile runtime --runtime-view json,ordo-code
```

У `json` mode `next-step --format auto` повертає звичайний report без code-like блоку.

У `ordo-code` mode `next-step --format auto` автоматично повертає `current_contract`.

У `json,ordo-code` mode можна явно обрати будь-який із двох форматів.

## Чому це важливо

Мета Ordo-code view не в тому, щоб зробити ще один runtime. Мета — покращити поведінку моделі:

```text
менше вигаданих переходів;
менше вільного трактування allowed answers;
краща кореляція між compiled project і відповіддю моделі;
видимий contract fragment у кожному кроці.
```

Але source of truth не змінюється:

```text
JSON IR вирішує.
Ordo-code пояснює.
```
