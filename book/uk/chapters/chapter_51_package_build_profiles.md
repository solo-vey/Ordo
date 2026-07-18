# Розділ 51. Package build profiles: dev / runtime / evidence

M56 додає в Ordo стандарт розділення package на три профілі.

## Навіщо це потрібно

Один subject package під час розробки може містити все одразу: source YAML, compiled IR, тести, run inputs, generated outputs, runtime snapshots і звіти. Для розробника це корисно, але для guided runtime це небезпечно: executor може випадково дивитися на YAML або старі проміжні файли замість актуального `compiled/program.ir.json`.

Тому вводяться три профілі:

```text
dev      — повний source package для розробки та аудиту
runtime  — чистий executable package для guided intake
evidence — докази компіляції, валідації, hash/provenance/status
```

## Runtime profile

Runtime package має працювати без editable YAML:

```text
README.md
START_HERE_RUNTIME_MODE.md
START_PROMPT_RUNTIME_MODE.md
ordo.runtime.json
compiled/program.ir.json
output_templates/
reports/CLI_VALIDATION_SUMMARY.md
reports/BUILD_MANIFEST.json
reports/SHA256SUMS.txt
```

Він не має містити:

```text
source/program.ordo.yaml
tests/
run_inputs/
domain/
runtime/state_snapshots/
generated_outputs/
release/*.zip
```

Головне правило:

```text
Runtime package must not require source YAML for execution.
Runtime package must use compiled/program.ir.json as primary runtime source.
```

## CLI

Пакування виконується явно:

```bash
ordo package <package> --profile dev --out <zip>
ordo package <package> --profile runtime --out <zip>
ordo package <package> --profile evidence --out <zip>
```

Для runtime-профілю CLI перевіряє наявність compiled IR, свіжість IR відносно YAML, runtime start files, output templates і CLI evidence.

## Evidence

Кожен build profile генерує або використовує:

```text
reports/BUILD_MANIFEST.json
reports/SHA256SUMS.txt
reports/package_report.json
```

Runtime profile також генерує:

```text
ordo.runtime.json
```

Це дає executor-у чистий runtime package, а reviewer-у — окремий evidence package.

PDF книги не перегенеровувався в M56.


## Стандартні помилки package profiles

```text
ORDO-PACKAGE-001 unknown package profile
ORDO-PACKAGE-002 runtime profile includes source YAML
ORDO-PACKAGE-003 runtime profile missing compiled IR
ORDO-PACKAGE-004 runtime profile missing output templates
ORDO-PACKAGE-005 runtime profile missing START_HERE_RUNTIME_MODE.md
ORDO-PACKAGE-006 runtime profile missing ordo.runtime.json
ORDO-PACKAGE-007 runtime profile missing BUILD_MANIFEST.json
ORDO-PACKAGE-008 runtime profile missing SHA256SUMS.txt
ORDO-PACKAGE-009 evidence profile includes editable source files
ORDO-PACKAGE-010 package claims executed_cli_passed without CLI evidence
```
