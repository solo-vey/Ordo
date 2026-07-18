# README — передача поточного стану ORDO / ARF

## Що це за пакет

Це transfer-пакет для продовження роботи в новому чаті. Він містить **повне максимально відновлене дерево ORDO/ARF**, отримане 2026-07-14, плюс окремий каталог `TRANSFER_2026-07-14/` із контекстом саме цього діалогу.

Критично: пакет **не є byte-identical фінальним canonical BL-ORDO-032 baseline**. Після втрати активного workspace ми відновилися з останнього повного BL-ORDO-027 baseline і наклали доступні closure/backlog/instruction artifacts. Частина source-level змін BL-ORDO-032 відома лише за closure evidence і описом діалогу.

## Як читати — обов'язковий порядок

1. `TRANSFER_2026-07-14/CURRENT_DIALOG_STATE_UK.md` — де зупинився діалог і що робити далі.
2. `TRANSFER_2026-07-14/RECOVERY_AND_TRUST_STATUS_UK.md` — що відновлено точно, а що не можна вважати відновленим byte-for-byte.
3. `TRANSFER_2026-07-14/BACKLOG_DETAILED_UK.md` — детальний backlog зі статусами `done/open/partial/uncertain`.
4. `TRANSFER_2026-07-14/BACKLOG_RELATED_FILES_INDEX_UK.md` — які файли належать до backlog/status governance.
5. `TRANSFER_2026-07-14/ANTIPATTERN_REFERENCE_INDEX_UK.md` — anti-pattern corpus, каталоги, приклади, fixtures, runtime binding і reports.
6. Лише після цього читати canonical/recovered package files.

## Правило для наступного чату

Не заявляти, що BL-ORDO-032 source tree відновлено byte-identical. Closure evidence існує, але exact final tree і durable 477-node checkpoint втрачено. Перед source implementation BL-ORDO-029 рекомендовано спочатку відновити BL-ORDO-032 source delta або повторно реалізувати його за closure evidence та провести full gate.

## Найближча продуктова задача

`BL-ORDO-029 — Inbound Transition Provenance Gate`.

Ідея: вузол повинен описувати не лише куди з нього дозволено перейти, а й **з яких безпосередніх вузлів дозволено входити в нього**. При вході runtime перевіряє provenance попереднього вузла. Валідатор дерева двосторонньо перевіряє кожне пряме ребро.
