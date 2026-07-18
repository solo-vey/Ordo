# Історична подія: `LU_CHANGE_EMAIL`

## 1. Бізнес-сенс

`LU_CHANGE_EMAIL` фіксує зміну email компанії у профілі ЄДР. Користувач має бачити, що контактна електронна адреса компанії змінилася, а також старе і нове значення.

Подія вже реалізована в продукті. Цей паспорт фіксує підтверджений контракт і є Confluence-ready сторінкою для handoff.

## 2. Джерело даних і QA/dev fixture

| Поле | Значення |
|---|---|
| Джерело | попередній analysis package + підтверджений Mongo/dev row |
| collection | `cards` |
| bootstrap/debug mongoId | `69b83e3aa194013118aa83c7` |
| root_id | `c_c204ad07-22d1-11f1-8032-5955027482c1` |
| dms_id | `UACA409857303` |
| type/sub_type | `companyProfile` / `EDR` |
| Поточний email | `donor.sumy@gmail.com` |
| Новий QA email | `qa.change.email@example.com` |
| Rollback email | `donor.sumy@gmail.com` |

`dms_id` не змінюється при зміні запису і використовується як стабільний matcher у source lookup. Окремий placeholder для clean fixture DMS не потрібен.

## 3. Технічний контракт

| Параметр | Значення |
|---|---|
| Alias / ChangeType | `LU_CHANGE_EMAIL` |
| Provider | `CompanyProfileHistoryEventProducer` |
| Rule | `LuChangeEmailHistoryEventRule` |
| Logical change type | `UPDATE` / `modified` |
| Trigger field | `contacts.email` |
| Old source | `prevData.item.contacts.email` |
| New source | `data.item.contacts.email` |
| Values | `old#email`, `new#email` |
| Кількість events | `0..1` для одного `ChangeRecord` |

## 4. Values mapping

| Key у `HistoryEvent.item.values` | Джерело | Правило |
|---|---|---|
| `old#email` | `prevData.item.contacts.email` | display/original після `trim`; missing/null/blank → `—` |
| `new#email` | `data.item.contacts.email` | display/original після `trim`; missing/null/blank → `—` |

Generic keys `old#value` / `new#value` не використовуються.

## 5. Нормалізація

Для порівняння використовується `trim + lower-case`.

Для запису в `values` зберігається display/original значення після `trim`, без примусового `lower-case`.

Подія не створюється, якщо:

- старий і новий email однакові після `trim + lower-case`;
- змінилося не `contacts.email`;
- обидві сторони missing/null/blank.

## 6. Manual QA test cases

| ID | Сценарій | Дія | Очікування |
|---|---|---|---|
| TC-01 | Реальна зміна email | `donor.sumy@gmail.com` → `qa.change.email@example.com` | Створено `LU_CHANGE_EMAIL` з `old#email/new#email` |
| TC-02 | Зміна тільки регістру | `donor.sumy@gmail.com` → `Donor.Sumy@gmail.com` | `LU_CHANGE_EMAIL` не створюється |
| TC-03 | Зміна тільки крайніх пробілів | `donor.sumy@gmail.com` → ` donor.sumy@gmail.com ` | `LU_CHANGE_EMAIL` не створюється |
| TC-04 | Email очищено | `donor.sumy@gmail.com` → empty string | Створено `LU_CHANGE_EMAIL`, `new#email=—` |
| TC-05 | Зміна іншого contact field | `contacts.fax` змінено | Саме `LU_CHANGE_EMAIL` не створюється |

Детальні кроки для тестувальника містяться у `05_QA_PACKAGE_LU_CHANGE_EMAIL.md`.

## 7. Unit/provider test requirements

| ID | Сценарій | Очікування |
|---|---|---|
| UNIT-TC-01 | `contacts.email` змінився | створюється `LU_CHANGE_EMAIL` |
| UNIT-TC-02 | case-only / trim-only зміна | подія не створюється |
| UNIT-TC-03 | blank/missing з одного боку | event із placeholder `—` |
| UNIT-TC-04 | `delta.field` не `contacts.email` | `LU_CHANGE_EMAIL` не створюється |

## 8. Traceability matrix

| Бізнес-вимога | Passport section | Jira AC | Manual QA TC | Automation TC | Unit/provider TC | Коментар |
|---|---|---|---|---|---|---|
| Показувати реальну зміну email | 3-5 | AC-1..4 | TC-01 | AUTO-TC-01 | UNIT-TC-01 | values `old#email/new#email` |
| Ігнорувати case-only зміну | 5 | AC-5 | TC-02 | AUTO-TC-02 | UNIT-TC-02 | `trim + lower-case` |
| Ігнорувати trim-only зміну | 5 | AC-5 | TC-03 | AUTO-TC-03 | UNIT-TC-02 | крайні пробіли незначущі |
| Підтримати очищення email | 4-5 | AC-6 | TC-04 | AUTO-TC-04 | UNIT-TC-03 | `new#email=—` |
| Не створювати email event для fax | 3,6 | AC-7 | TC-05 | AUTO-TC-05 | UNIT-TC-04 | інше contact field |
| Manual QA за V26.48.2 | 9 | AC-8..12 | TC-01..TC-05 | AUTO-TC-01..05 | n/a | projection, patch, rollback |

## 9. QA execution contract

Manual QA використовує:

```text
POST /api/test/product-queue/publish-mongo-patch
POST /api/history
```

У ручних REST-запитах `ClientSecret` не додається за замовчуванням.

Source lookup виконується через `root_id + dms_id + type + sub_type`; `mongoId` використовується як bootstrap/debug value.

## 10. Out of scope

- Не змінювати інші contact events: `LU_CHANGE_FAX`, `LU_CHANGE_PHONE`, `LU_CHANGE_WEB`.
- Не змінювати monitoring handler-и або monitoring documentation.
- Не змінювати `DefaultHistoryEventProducer`.
- Не змінювати структуру `ChangeRecord` або `HistoryEvent`.
- Не додавати службовий `internal` сегмент у data-import endpoint-и.
- Не використовувати full item replacement там, де достатньо field patch.
