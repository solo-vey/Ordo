# Розділ 48. Runtime source of truth і чесність CLI

Після появи contract → artifact coverage і two-tier rendering Ordo отримав ще один важливий шар: runtime source of truth.

Ідея проста: Ordo package не можна виконувати як випадковий набір файлів. Його треба завантажувати як послідовний runtime:

```text
ordo.yml → source/program.ordo.yaml → compiled/program.ir.json → run_state.json → generated_outputs/
```

`ordo.yml` є входом у пакет. `source/program.ordo.yaml` є редагованим source of truth. `compiled/program.ir.json` є runtime-артефактом, з якого helper-команди мають брати Process Rail, вузли, gates і outputs. `run_state.json` або report із вкладеним `state` описує поточний стан виконання. Generated artifacts — це вже результат rendering.

## Чому це потрібно

Без цього правила AI Ordo Developer може випадково вести guided intake “за памʼяттю”: почати не з того питання, пропустити gate або використати старі інструкції після зміни YAML.

M53 закриває цей клас помилок: якщо YAML новіший за compiled IR, runtime helper має блокувати виконання і просити перекомпілювати пакет.

```text
ORDO-RUNTIME-004: IR is stale. Run ordo compile before guided execution.
```

## Стандартний Developer workflow

```text
runtime-status
lint
compile
test
coverage
validate-state
check-gate / next-step
generate-output
validate-output
validate-artifacts
consistency
go-no-go
package
```

Важливо: `compile` не означає, що фінальний пакет валідний. Він лише створює Semantic JSON IR. Фінальна готовність визначається після validate-artifacts, consistency і go-no-go.

## Чесність CLI

Ordo також вводить правило truthfulness: модель не має писати “CLI validation passed”, якщо CLI реально не запускався.

Дозволені статуси:

```text
executed_cli_passed
executed_cli_failed
logical_self_check_only
not_run_cli_unavailable
not_run_user_skipped
```

Це відділяє реальну перевірку від логічного припущення. Якщо CLI недоступний, це не помилка — але це треба чесно вказати.

## Що це дає

M53 робить Developer Bundle ближчим до справжнього runtime-пакета: AI працює гнучко, але кожен критичний перехід перевіряється детерміновано.
