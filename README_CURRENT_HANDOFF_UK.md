# Поточний архів мовного проєкту Ordo

Дата збирання: 2026-07-12

## Що містить пакет

- повний поточний working tree мовного проєкту;
- CLI, schemas, registries, lint rules, tests, utilities та книги;
- `CONSOLIDATED_BACKLOG.md` — актуальний backlog;
- M87 benchmark implementation і closure evidence;
- реальні API-results двох моделей та blind-scoring evidence для BL-ORDO-018;
- reference intake для BL-ORDO-020.

## Поточний стан

- BL-ORDO-016 — closed;
- BL-ORDO-017 — closed;
- BL-ORDO-018 — `closed-qualified` at M87.6;
- BL-ORDO-023 — open, strict-zero A/B revalidation;
- BL-ORDO-020 — наступний великий implementation track;
- BL-ORDO-021, BL-ORDO-022 та BL-ORDO-008 — open;
- BL-ORDO-015 формально open до GitHub CI closure.

## Як читати пакет

1. Почати з цього README.
2. Відкрити `CONSOLIDATED_BACKLOG.md`.
3. Для поточного M87 дивитися `reports/m87_external_evidence/`.
4. Для benchmark raw evidence дивитися `evidence/bl_ordo_018/`.
5. Для наступної роботи перейти до BL-ORDO-020.

## Важлива кваліфікація

BL-ORDO-018 закрито з practical non-inferiority margin `-0.10 / 100`. Сувора межа `0.00` винесена в BL-ORDO-023.
