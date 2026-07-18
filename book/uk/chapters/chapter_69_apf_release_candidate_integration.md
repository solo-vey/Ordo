# Розділ 69. M63: інтеграція APF release-candidate

M63 відкриває окрему лінію інтеграції `ordo.applied_project_factory` як release-candidate стандартного прикладного модуля.

Важливо: APF не стає частиною runtime core. Це стандартний прикладний модуль, який використовує Ordo для створення інших playbook/process packages.

## Що фіксує M63.0

- M62 містив APF `v0.1.0-alpha.14` як historical import point.
- Ціль M63 — APF `v0.1.0-rc.1`, source base `alpha.21`.
- Патерни APF класифікуються обережно: не всі вони стають IR/opcode.
- `FLOW.JOIN` і `SHARED.TAIL.REFERENCE` лишаються future IR candidates.
- `validate-factory-output` лишається APF-local або optional, доки не буде стабільної parent-CLI семантики.

## Чому це окрема лінія

M62 закрив інтеграцію APF як стандартного модуля на рівні пакета. M63 має зробити release-candidate приймання: оновити пакет, метадані, validation profile, known limitations і classification matrix.

## Межа

M63.0 не переписує APF YAML, не змінює runtime core і не додає нові opcodes. Це planning/delta-review gate перед імпортом rc.1.
