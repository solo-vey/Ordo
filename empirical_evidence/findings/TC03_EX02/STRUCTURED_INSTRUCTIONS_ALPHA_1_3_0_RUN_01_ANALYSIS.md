# Structured Instructions Alpha 1.3.0 — RUN_01 analysis

## Об’єкт

- Representation: `Structured Instructions — narrative process`
- Package: `ORDO_STRUCTURED_INSTRUCTIONS_NARRATIVE_PROCESS_ALPHA_1_3_0_AUTOMATED_TESTING.zip`
- Run evidence: `ORDO_RUN_01_FULL_FIDELITY_EVIDENCE.zip`
- Scenario: `RUN_01`

## Результат

| Metric | Score |
|---|---:|
| Process | 94 |
| Passport | 96 |
| Jira | 94 |
| Manual QA | 97 |
| Automation | 96 |
| Documents | 96 |
| Final | 95 |

Terminal route: `T_COMPLETED / go`.

## Що підтверджено

- ZIP структурно справний.
- Driver реально запускав авторитетні валідатори.
- Збережено validator IDs, команди, stdout/stderr, return codes та artifact hashes.
- Correction loops фактично відпрацювали: Passport, Jira, Manual QA й Automation були виправлені та повторно перевірені.
- Фінальні документи змістовно повні й придатні до оцінювання.
- Model-authored PASS receipts не використовувалися як достатній доказ.

## Зафіксований дефект пакування доказів

`SHA256SUMS.txt` помилково містить checksum самого себе:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  SHA256SUMS.txt
```

Фактичний файл не порожній, тому повна команда `sha256sum -c SHA256SUMS.txt` завершується попередженням про одну невідповідність. Усі інші записи manifest пройшли.

Це дефект final evidence package assembly, а не дефект змісту Structured Instructions або аналітичної поведінки Driver.

## Рішення для бенчмарку

- RUN_01 прийнято як змістовно успішний запуск із Final score **95**.
- Результат позначено як `PASS_WITH_PACKAGE_ASSEMBLY_DEFECT`.
- Для наступних запусків `SHA256SUMS.txt` не повинен включати власний checksum. Зовнішній checksum ZIP має зберігатися окремим `.sha256` файлом.
- Повна серія Alpha 1.3.0 ще не завершена: RUN_02–RUN_05 очікуються.
