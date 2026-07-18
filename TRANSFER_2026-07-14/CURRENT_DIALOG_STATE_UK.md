# Поточний стан діалогу

## Де ми зупинилися

1. BL-ORDO-032 був доведений у діалозі до closure evidence: заявлено 477/477 pytest nodes passed, 4/4 package lints passed, blocking=0, canonical pre/post hash equal.
2. Після цього активний canonical workspace було втрачено/він став недоступним.
3. Ми відновили дерево з останнього доступного повного архіву BL-ORDO-027 і наклали доступні closure/recovery/backlog artifacts.
4. Відновлений пакет чесно класифікований як `maximally_recovered_integration_candidate`, не canonical byte-identical BL-ORDO-032.
5. Користувач вирішив перейти до BL-ORDO-029, але перед початком попросив зробити повний transfer package цього діалогу.

## Що було зроблено в BL-ORDO-032 у діалозі

Розроблено/діагностовано hermetic non-destructive delivery gate:
- canonical workspace protection;
- disposable workspace lifecycle;
- pre/post integrity guard;
- write-boundary enforcement;
- destructive-test detector;
- partition isolation;
- failure classification;
- recovery protocol;
- archive provenance;
- hermetic delivery regression suite;
- book impact / English book sync;
- partitioned gate;
- per-file checkpoint runner;
- process-group cleanup;
- bounded subprocess timeout;
- file-backed stdout/stderr;
- post-summary lifecycle handling;
- `passed_with_forced_teardown`;
- split великих smoke/CLI workflow test files;
- перехід до per-test-node hermetic checkpoint execution.

У діалозі було заявлено фінальний green: 477/477 nodes, 4/4 lints, blocking=0.

## Відомі source fixes BL-ORDO-032

За closure history:
- видалення 10 generated anti-pattern reports із canonical source tree;
- generated reports мають жити у disposable gate/release evidence workspace;
- backlog sync fix;
- generated report isolation fix;
- APF graph/linter fixes;
- `on_unmatched_input` для migration nodes;
- підтримка `flow_reuse` і `runtime_capabilities`;
- milestone reports moved to `archive/milestone_reports/`;
- hardened delivery runner;
- node-level checkpointing.

Точні фінальні байти частини цих змін втрачено.

## BL-ORDO-029 — прийнята концепція

Для кожного node:
- outbound transitions залишаються;
- додається inbound predecessor contract (`allowed_from` / canonical name to be designed);
- при вході node runtime спочатку перевіряє, звідки прийшов execution;
- якщо predecessor не дозволений — normal node execution не починається;
- запускається transition provenance diagnosis/recovery;
- перевіряються лише direct one-hop edges;
- validator перевіряє A→B у двох напрямках:
  1. A реально має outbound edge до B;
  2. B реально дозволяє inbound from A;
- inbound-only і outbound-only edge mismatch — blocking;
- окремо спроєктувати root/resume/retry/recovery/migration semantics.

## Наступний рекомендований порядок

1. Прочитати recovery status.
2. Перевірити exact baseline checksums.
3. Відновити/повторно реалізувати BL-ORDO-032 source delta.
4. Запустити full gate та створити новий canonical baseline.
5. Почати BL-ORDO-029 із contract/schema design.
