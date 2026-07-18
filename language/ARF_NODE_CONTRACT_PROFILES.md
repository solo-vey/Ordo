# ARF Node Contract Profiles v1

Status: implemented for BL-ORDO-027 step 2.

Кожен executable node має оголосити рівно один профіль. Профіль визначає мінімальний contract і не дозволяє вузлу непомітно брати іншу відповідальність.

## Профілі

- `routing_node` — лише вибір явного маршруту.
- `capture_node` — лише приймання або нормалізація вводу.
- `execution_node` — одна atomic allowlisted дія.
- `validator_node` — незалежна machine-checkable validation.
- `authorization_node` — одне підтвердження для однієї дії та scope.
- `terminal_node` — фінальний статус лише з mandatory evidence.

## Загальні правила

1. Unknown profile або action → `blocked_missing_instruction`.
2. Якщо вузол потребує двох профілів, його треба розділити.
3. Routing не виконує роботу; execution не валідовує себе; validator не змінює target.
4. Authorization не успадковується між responsibility domains.
5. Terminal status визначається найслабшою mandatory перевіркою.

## Артефакти

- `language/schemas/arf_node_contract.schema.json`
- `language/registry/arf_node_contract_profiles.v1.json`
- `language/examples/arf_node_contract_profiles.examples.json`
