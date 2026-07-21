# ORDO / ARF — максимально нове відновлення станом на 2026-07-14

## База

Відновлення побудоване з останнього доступного повного архіву:

`ORDO_ARF_BL_ORDO_027_CLOSED_BOOK_SYNC_2026-07-13.zip`

SHA-256 вихідного baseline:

`5911195cdd7977df49e4540b07d8d2507778ab137e7233c9b1d2d58a83049a01`

Baseline містив 3583 файли та повне дерево `cli/`, `packages/`, `schemas/`, `language/`, `book/`, tests, manifests і reports.

## Що вдалося накласти поверх baseline

1. Повний стан BL-ORDO-027 із post-closure book sync — уже був у baseline.
2. Closure evidence BL-ORDO-032:
   - root `reports/delivery/current/DELIVERY_GATE_REPORT.json`;
   - JSON/Markdown closure reports у `reports/bl_ordo_032/`.
3. Відновлений backlog-контракт BL-ORDO-029:
   - inbound predecessor allowlist;
   - runtime entry provenance gate;
   - двостороння перевірка кожного прямого ребра;
   - direct-edge-only semantics;
   - окремі правила для root/resume/retry/recovery/migration.
4. Два прийняті instruction-source документи для deterministic control/context reload у `recovery/2026-07-14/source_delta/`.
5. Запис BL-ORDO-032 у Markdown і JSON backlog як `closed_with_recovered_evidence`.

## Що не вдалося відновити byte-for-byte

Нижче наведені зміни були виконані або описані після baseline, але точні остаточні файли відсутні в активному runtime:

- остаточна інтегрована версія `tools/build_release_archive.py` з per-test-node hermetic runner;
- durable checkpoint повного 477-node gate;
- точні source edits усіх timeout/process-group/post-summary lifecycle hardening кроків;
- фізичне розбиття великих CLI workflow tests на остаточний набір файлів;
- видалення 10 generated anti-pattern reports з canonical source tree та всі залежні checksum edits;
- точні APF graph/linter source changes (`on_unmatched_input`, `flow_reuse`, `runtime_capabilities` та пов'язані aliases/contracts);
- точний перенос milestone reports у `archive/milestone_reports/`;
- точні синхронізації backlog/maturity/manifest, виконані під час BL-ORDO-032 closure;
- повний набір нових regression tests для lingering process, signal cleanup, per-node checkpointing та report provenance;
- exact final canonical tree hash, заявлений closure evidence, не може бути відтворений з доступних байтів.

## Наслідок

Цей архів є **maximally recovered integration candidate**, а не byte-identical фінальним архівом BL-ORDO-032.

Перед продовженням BL-ORDO-029 потрібно:

1. перевірити baseline checksums;
2. повторно реалізувати або відновити перелічені source-level BL-ORDO-032 зміни;
3. запустити повний gate;
4. лише після green gate позначити дерево як новий canonical baseline.
