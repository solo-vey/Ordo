# Jira task — привести до ладу історичну подію `LU_CHANGE_EMAIL`

## Summary

Привести аналітичний пакет, Jira-ready опис, ручні QA-інструкції та automation artifacts для вже реалізованої історичної події `LU_CHANGE_EMAIL` до актуальних вимог V26.48.2.

## Context

Подія `LU_CHANGE_EMAIL` уже реалізована в продукті. Ця задача не є greenfield-реалізацією нового alias-а.

Користувач має бачити в історії зміну контактного реквізиту “email”: старе значення і нове значення. Подія працює для `UPDATE`-сценарію профілю компанії, коли у `ChangeRecord.delta` зафіксовано зміну поля `contacts.email`.

Джерелом вимог є Confluence-ready паспорт:

```text
01_HISTORY_EVENT_PASSPORT_LU_CHANGE_EMAIL.md
```

Попередній архів був у старішому форматі й містив занадто коротку Jira-задачу. У цьому пакеті Jira-задачу потрібно використовувати як повноцінний handoff summary для менеджера, розробника і тестувальника, але без дублювання всього паспорта.

## Acceptance criteria

1. Створювати `LU_CHANGE_EMAIL`, якщо `data.status=modified`, `data.type=companyProfile`, `data.sub_type=EDR` і `delta.field=contacts.email`.
2. Старе значення брати з `prevData.item.contacts.email`.
3. Нове значення брати з `data.item.contacts.email`.
4. У `HistoryEvent.item.values` записувати тільки `old#email` і `new#email`; generic `old#value/new#value` не використовувати.
5. Якщо email відрізняється тільки регістром або крайніми пробілами, `LU_CHANGE_EMAIL` не створюється.
6. Якщо email очищено, створюється `LU_CHANGE_EMAIL` з `new#email=—`.
7. Якщо змінилося інше контактне поле, наприклад `contacts.fax`, саме `LU_CHANGE_EMAIL` не створюється.
8. Для валідних сценаріїв не створюються `change_errors`.
9. `05_QA_PACKAGE_LU_CHANGE_EMAIL.md` є повною ручною інструкцією: кожний TC містить конкретні Mongo/REST кроки, expected result і rollback.
10. Manual QA використовує Mongo projection і не виводить увесь `item`, якщо перевіряється тільки `contacts.email` або `contacts.fax`.
11. Manual REST-запити не містять `ClientSecret` за замовчуванням.
12. Field-change manual TC використовують `POST /api/test/product-queue/publish-mongo-patch`, а не full item replacement.
13. Rollback виконується точковим patch тільки зміненого поля.
14. `dms_id` використовується як стабільний source lookup matcher; окремий clean-fixture DMS placeholder не вводиться.
15. `08_QA_AUTOMATION_SPEC_LU_CHANGE_EMAIL.yaml` використовує root keys `suite/defaults/test_cases`.
16. Negative automation TC використовують `expected_events_absent`, а не `expected_events + expect_absent`.
17. Compact archive не містить окремих фінальних markdown-файлів `03/06/10/11`; їхній зміст перенесено в `01`, `09` і JSON reports.

## Data mapping

| Що | Значення |
|---|---|
| Alias | `LU_CHANGE_EMAIL` |
| Provider | `CompanyProfileHistoryEventProducer` |
| Rule | `LuChangeEmailHistoryEventRule` |
| Type/sub_type | `companyProfile` / `EDR` |
| Trigger | `delta.field=contacts.email` |
| Old source | `prevData.item.contacts.email` |
| New source | `data.item.contacts.email` |
| Old value key | `old#email` |
| New value key | `new#email` |
| Comparison normalization | `trim + lower-case` |
| Display normalization | `trim`; missing/null/blank → `—` |

## Technical deliverables

- Перевірити/підтвердити `ChangeType.LU_CHANGE_EMAIL`.
- Перевірити/підтвердити `LuChangeEmailHistoryEventRule`.
- Перевірити реєстрацію rule у `CompanyProfileHistoryEventProducer`.
- Перевірити unit/provider tests для `UNIT-TC-01..UNIT-TC-04`.
- Перевірити `.md` поруч із Java test class.
- Перевірити project passport `docs/history-events/company-profile-edr/LU_CHANGE_EMAIL.md`, якщо задача виконується як документаційна/кодова актуалізація модуля.
- Перевірити provider docs і supported-event registry, якщо такі реєстри є в модулі.
- Не змінювати monitoring, data-import REST contract, структуру `ChangeRecord`, структуру `HistoryEvent`, `application*.yml/yaml`.

## QA reference data

| Поле | Значення |
|---|---|
| collection | `cards` |
| bootstrap/debug mongoId | `69b83e3aa194013118aa83c7` |
| root_id | `c_c204ad07-22d1-11f1-8032-5955027482c1` |
| dms_id | `UACA409857303` |
| type/sub_type | `companyProfile` / `EDR` |
| current email | `donor.sumy@gmail.com` |
| new email | `qa.change.email@example.com` |
| case-only email | `Donor.Sumy@gmail.com` |
| trim-only email | ` donor.sumy@gmail.com ` |
| fax для negative TC | `+380501112233` |
| mutation endpoint | `POST /api/test/product-queue/publish-mongo-patch` |
| create-history trigger | `POST /api/history` |
| source lookup | `root_id + dms_id + type + sub_type` |

`dms_id` стабільний для цього source row. Після action і rollback source lookup має використовувати `dms_id`, `root_id`, `type`, `sub_type`; `mongoId` не вважати єдиним довгостроковим matcher-ом, якщо row може перестворюватися.

## Manual QA test cases для тестувальника

| TC | Сценарій | Тестові дані | Очікуваний результат |
|---|---|---|---|
| TC-01 | Реальна зміна email | `donor.sumy@gmail.com` → `qa.change.email@example.com` | створюється `LU_CHANGE_EMAIL` з `old#email=donor.sumy@gmail.com`, `new#email=qa.change.email@example.com` |
| TC-02 | Зміна тільки регістру email | `donor.sumy@gmail.com` → `Donor.Sumy@gmail.com` | `LU_CHANGE_EMAIL` не створюється |
| TC-03 | Зміна тільки крайніх пробілів email | `donor.sumy@gmail.com` → ` donor.sumy@gmail.com ` | `LU_CHANGE_EMAIL` не створюється |
| TC-04 | Email очищено | `donor.sumy@gmail.com` → empty string | створюється `LU_CHANGE_EMAIL` з `old#email=donor.sumy@gmail.com`, `new#email=—` |
| TC-05 | Змінилося інше contact field | змінити `contacts.fax` | саме `LU_CHANGE_EMAIL` не створюється |

Детальні покрокові інструкції: `05_QA_PACKAGE_LU_CHANGE_EMAIL.md`.

## Automation reference

`08_QA_AUTOMATION_SPEC_LU_CHANGE_EMAIL.yaml` автоматизує representative manual TC:

- positive TC через `expected_events`;
- negative TC через `expected_events_absent`;
- source lookup через стабільний `dms_id`;
- action/rollback через `publish-mongo-patch`.

Після цього перезбирання пакета live-run потрібно повторити.

## Out of scope

- Не змінювати поведінку `LU_CHANGE_FAX`, `LU_CHANGE_PHONE`, `LU_CHANGE_WEB` або інших contact events.
- Не додавати підтримку нових email-specific validation rules без окремого бізнес-рішення.
- Не змінювати shared matching у `DefaultHistoryEventProducer`.
- Не змінювати REST-контракти data-import.
- Не змінювати monitoring handler-и або monitoring documentation.
- Не додавати `ClientSecret` у manual QA requests за замовчуванням.
- Не використовувати full item replacement для простих field-change TC.

## Links

- Confluence-ready passport: `01_HISTORY_EVENT_PASSPORT_LU_CHANGE_EMAIL.md`.
- Manual QA package: `05_QA_PACKAGE_LU_CHANGE_EMAIL.md`.
- Automation README: `09_QA_AUTOMATION_README_LU_CHANGE_EMAIL.md`.
- Confluence URL after creation: `<CONFLUENCE_PAGE_URL_AFTER_CREATION>`.
