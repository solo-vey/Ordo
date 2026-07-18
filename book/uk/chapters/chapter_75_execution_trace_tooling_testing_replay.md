# Розділ 75. Перевірка, replay і практичне використання EXECUTION_TRACE

Після того як `EXECUTION_TRACE` став елементом мови та отримав runtime-семантику, його потрібно перевіряти так само суворо, як gates, state і generated outputs.

## Що потрібно тестувати

Мінімальний набір перевірок складається з шести шарів:

1. canonical YAML-приклади читаються і відповідають закритому каталогу значень;
2. компілятор створює рівно один `EXECUTION_TRACE.DEF`;
3. runtime створює append-only trace, правильно нумерує події та забороняє запис після terminal status;
4. integrity validation знаходить пропуски sequence, неправильний `event_count` і зміну checksum;
5. replay режими правильно керують повторним обчисленням і side effects;
6. секрети редагуються до запису на диск.

## Як читати trace

Людина читає trace зверху вниз як хронологію виконання. Для кожної події потрібно дивитися:

- де вона сталася (`location`);
- хто її виконав (`actor`);
- які дані були використані (`payload`);
- чи змінився state (`state_effect`);
- з яким gate, decision або output вона пов’язана (`correlation`);
- чим завершилася (`outcome`).

## Чотири способи replay

`deterministic` повторює збережені inputs і рішення. `re_evaluate` залишає inputs, але заново обчислює decisions та gates. `simulation` забороняє зовнішні side effects. `audit_only` нічого не виконує і лише відтворює історію для перевірки.

Для аналізу поведінки аналітика або навчання достатньо `audit_only`. Для regression testing найчастіше потрібні `deterministic` і `simulation`.

## Як виявляється зміна trace

Після terminal event runtime обчислює checksum canonical представлення trace. Якщо хтось змінить payload, sequence, event count або іншу частину історії, повторно обчислений checksum не збігатиметься. Це не цифровий підпис і не заміна захищеного сховища, але це надійний контроль випадкової або непогодженої зміни artifact-а.

## Що не входить у trace

`EXECUTION_TRACE` не зберігає приватний chain-of-thought моделі. Він зберігає тільки observable decision summary, reason code, evidence references і фактичні переходи процесу. Паролі, токени та інші секрети мають бути redacted або замінені secure reference до серіалізації.

## Практичне правило

```text
Trace корисний лише тоді, коли його можна перевірити, безпечно зберігати і відтворювати за чітко визначеним режимом.
```
