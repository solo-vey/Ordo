# Jira Task — {{ state.event_alias }}

> Generated from Ordo template `JIRA_TASK`.

## Title

Implement HistoryEvent `{{ state.event_alias }}` — {{ state.display_name_en }}

## Business scope

Create/update HistoryEvent logic for:

- UA name: {{ state.display_name_uk }}
- EN name: {{ state.display_name_en }}
- Path: `{{ state.selected_path }}`
- Source field(s): `{{ state.source_field }}`

## Trigger / value contract

{{ state.value_semantics | bullets }}

## Test deliverables

The implementation must include:

- Manual QA scenarios for confirmed positive and negative trigger cases.
- Functional tests for the confirmed business trigger behavior.
- Unit tests for all confirmed normal and corner cases when unit coverage is selected.
- Unit tests for null, missing object, missing field, empty string, spaces, trim, case normalization, and no-op scenarios when applicable.
- Unit tests for value-only, currency-only/field-only, and combined field changes when applicable.
- Unit tests for mixed delta where target fields are present together with unrelated fields when applicable.
- Markdown documentation for the Java test class, stored next to the test class with the same name and `.md` extension, when Java unit tests are required.
- {{ state.test_documentation_requirement }}

Confirmed test strategy:

{{ state.test_strategy_contract | bullets }}

## Acceptance criteria

- [ ] HistoryEvent is created for all confirmed positive trigger cases.
- [ ] HistoryEvent is not created for all confirmed negative/no-op cases.
- [ ] Manual QA package covers positive and negative trigger cases, including empty/null/missing transitions.
- [ ] Functional tests cover the confirmed trigger behavior.
- [ ] Extended unit tests cover all confirmed corner cases when `Test coverage level` requires extended unit coverage.
- [ ] Test class markdown documentation is created or updated when Java unit tests are required.
- [ ] Rollback steps restore current state only and are not treated as a separate business verification scenario.

## Test coverage level

```text
{{ state.test_coverage_level }}
```
