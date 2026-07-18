# Розділ 80. Session Package Load and Cache

У довгих APF/playbook-сесіях з'явилася практична проблема: модель могла на кожному кроці знову розпаковувати archive і перечитувати package files.

```text
unpack → read → execute one step
→ unpack → read → execute next step
```

Це повільно, створює шум і збільшує ризик того, що різні кроки спиратимуться на різні прочитані fragments.

M80 вводить session package load-and-cache contract.

## Load once

Після першого успішного package-read pass runtime фіксує:

```text
package_loaded
package_version
package_fingerprint
unpacked_location
manifest_validated
source_of_truth_loaded
```

Якщо package version і fingerprint не змінилися, validated package використовується повторно в межах поточної session.

## Reload conditions

Повторний unpack/read потрібен лише коли:

```text
new package version supplied
fingerprint changed
runtime cache lost
required file missing
manifest validation failed
explicit full reload requested
```

## Cache hit

Правильний runtime flow:

```text
MESSAGE_RECEIVED
→ PACKAGE_CACHE_CHECK
→ cache valid: use loaded baseline
→ cache invalid: unpack + validate + load
→ ACTIVE_NODE_EXECUTION
```

Після valid cache hit повторний full unpack/read заборонений.

## Trace і diagnostics

Runtime фіксує події:

```text
PACKAGE_CACHE_HIT
PACKAGE_RELOAD_REQUIRED
PACKAGE_LOADED
PACKAGE_CACHE_INVALID
```

Metrics і diagnostics дозволяють побачити зайві reload-и та причину invalidation.

## Рівень APF і playbook

Механізм fingerprint, cache validation, reload conditions і trace events належить APF/runtime contract.

Конкретний playbook може містити коротку інструкцію не перечитувати factory package на кожному кроці, але не повинен сам винаходити cache semantics.

Головний принцип M80:

```text
validate once;
reuse while fingerprint is stable;
reload only for an explicit reason;
record cache behavior in trace.
```
