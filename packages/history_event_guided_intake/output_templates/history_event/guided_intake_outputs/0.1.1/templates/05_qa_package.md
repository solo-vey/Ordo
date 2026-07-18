# QA Package — {{ state.event_alias }}

> Generated from Ordo template `QA_PACKAGE`.

## QA scope

{{ state.qa_scope | bullets }}

## Value semantics contract

{{ state.value_semantics | bullets }}

## Confirmed test strategy

{{ state.test_strategy_contract | bullets }}

## Manual QA coverage

{{ state.manual_qa_coverage | bullets }}

## Functional test coverage

{{ state.functional_test_coverage | bullets }}

## Unit test coverage

{{ state.unit_test_coverage | bullets }}

## Required negative/no-op coverage

- no event for unchanged values after normalization;
- no event for null → null;
- no event for missing → null;
- no duplicate event for grouped changes in one ChangeRecord;
- unrelated delta fields do not trigger this event.

## Empty/null/missing transitions

- empty/null/missing → value must be tested as a positive trigger when business value appears;
- value → empty/null/missing must be tested as a positive trigger when business value disappears;
- null/missing → null must be tested as no-op.

## Rollback policy

- Rollback is technical restoration only; it is not a separate business verification scenario.

## Gate summary

```yaml
total: {{ gate_summary.total }}
passed: {{ gate_summary.passed }}
pending: {{ gate_summary.pending }}
blocked: {{ gate_summary.blocked }}
```
