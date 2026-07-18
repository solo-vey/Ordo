# Розділ 42. Зовнішній аудит pre-release пакета

Ordo будується навколо простої ідеї: не достатньо сказати, що процес валідний; потрібно показати, як саме це перевірити.

Саме тому після появи contract/artifact coverage, rendered artifact validation, consistency report і go/no-go pipeline потрібен ще один шар — зовнішній аудит пакета. Це не нова частина мови і не новий runtime. Це практичний спосіб передати пакет іншій людині або іншій AI-сесії і сказати: “не довіряй нашим звітам, перевір сам”.

## Що таке external audit package

External audit package — це набір інструкцій для незалежної перевірки Ordo workspace.

Він відповідає на питання:

- що саме має бути в архіві;
- яких старих каталогів уже не повинно бути;
- які CLI-команди треба запустити;
- які reference packages мають пройти перевірки;
- як перевірити generated artifacts;
- як перевірити consistency і go/no-go;
- які обмеження пакета не можна приховувати.

Це важливо, бо Ordo не має перетворювати validation report на акт віри. Звіт має бути доказом, який можна повторити.

## Чому цього недостатньо робити вручну

Якщо попросити reviewer-а просто “подивитися пакет”, кожен дивитиметься по-своєму. Один прочитає README. Інший запустить тільки lint. Третій подивиться на book source, але не перевірить CLI.

Тому M46.8 вводить не новий runtime, а стандартний маршрут перевірки:

```text
archive structure
→ CLI install
→ repo-check
→ unit tests
→ active package checks
→ generated artifact validation
→ consistency
→ go-no-go
→ audit verdict
```

Це робить зовнішню перевірку повторюваною.

## Що має перевірити reviewer

Reviewer має перевірити не тільки те, що код не падає. Він має перевірити відповідність обіцянки і поведінки.

Наприклад:

- якщо README каже, що legacy site/catalog/playbook root видалено, архів не має містити ці каталоги;
- якщо CLI каже, що `ordo test` — static mode, це має бути видно у виводі;
- якщо package має confirmed contracts, вони мають дійти до Passport, Jira, QA Package, Implementation Prompt і JSON reports;
- якщо `go-no-go` повертає `go`, має бути зрозуміло, які deterministic checks це підтвердили.

## Чесна межа Ordo preview

External audit також має перевіряти чесність обмежень.

Поточний Ordo preview не виконує live AI reasoning, REST-виклики, Mongo-перевірки або production business runtime. CLI є deterministic helper layer. Він перевіряє структуру, references, coverage, rendered artifacts, consistency і go/no-go report.

Це не слабкість, якщо про це сказано прямо. Слабкість була б у тому, щоб називати static validation повноцінним production runtime.

## Практичний результат

Після M46.8 Ordo package можна передати в іншу сесію з готовим prompt-ом аудиту. Reviewer має повернути короткий verdict:

```text
go
no_go
go_with_warnings
```

і пояснити, які команди він запускав, які артефакти дивився, які blocking issues або warnings знайшов.

Це робить pre-release перевірку не одноразовою дією автора, а відтворюваним процесом.



## Важливий порядок команд

`ordo repo-check` перевіряє чистоту source archive. Тому його потрібно запускати на чисто розпакованому пакеті до `pip install -e .` і до тестів, бажано як `PYTHONDONTWRITEBYTECODE=1 ordo repo-check ..`, щоб сам запуск Python не створив `__pycache__`. Після install або test у дереві можуть зʼявитися `__pycache__` та `egg-info`, і тоді source-hygiene перевірка справедливо впаде. Це не blocker, якщо перед фінальним пакуванням generated metadata знову прибрано.

## M46.9: самопрогін external audit checklist

M46.9 не додає нової мовної логіки. Його задача — взяти checklist з M46.8 і прогнати пакет як pre-release candidate: структура архіву, CLI, active packages, generated artifact validation, consistency, go-no-go, документація і book source.

Важливий результат M46.9: audit не має довіряти `M*_VALIDATION_REPORT.json` сам по собі. Він має або виконати команди, або явно зафіксувати, що команда не запускалася. Для Ordo це принципово: self-report не є доказом без перевірки.

Під час M46.9 було виявлено дрібну documentation-hygiene розбіжність: checklist очікував файл `cli/docs/GO_NO_GO_M46_5.md`, тоді як canonical CLI doc уже називався `cli/docs/GO_NO_GO.md`. Це не runtime blocker, але для pre-release audit такі речі мають бути виправлені, бо reviewer не повинен здогадуватися, який документ правильний.

Практичне правило після M46.9:

```text
repo-check → install CLI → tests → active packages → generated artifact flow → go-no-go → audit report
```

Якщо всі етапи проходять, пакет може отримати verdict `go` для source-available pre-release candidate. Це все ще не означає production runtime: Ordo CLI перевіряє deterministic structure, contracts, artifacts і consistency; він не виконує AI-модель, REST, Mongo або реальний бізнесовий backend.
