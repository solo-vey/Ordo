# APF rc.1 validation profile

У цьому кроці APF `v0.1.0-rc.1` лишається стандартним прикладним модулем у мовному пакеті Ordo.

Головне рішення: APF не провалюється через відсутність `validate-factory-output` у батьківському CLI. Ця перевірка поки вважається APF-local / optional, доки її не буде формально піднято до parent CLI.

Обовʼязковий профіль для rc.1:

```text
lint
compile
test
coverage
validate-state
next-step
validate-output
validate-artifacts
consistency
go-no-go
repo-check clean source
```

`consistency: passed_with_warnings` не приховується і не стає blocker-ом, якщо `go/no-go = go`. Попередження стосуються contract/default-value coverage і мають лишатися видимими в release notes та validation reports.

Цей крок не змінює APF logic, не додає нові IR/opcodes і не переносить APF-local patterns у core runtime.
